"""Telescope Firefox lifecycle — one live Firefox, context per job, recycle, relaunch."""

from __future__ import annotations

import pytest

pytest.importorskip("playwright")

import browser as browser_mod  # noqa: E402


class _FakeContext:
    def __init__(self) -> None:
        self.closed = False

    async def new_page(self):
        return object()

    async def close(self) -> None:
        self.closed = True


class _FakeBrowser:
    def __init__(self) -> None:
        self.alive = True
        self.closed = False
        self.contexts: list[_FakeContext] = []

    def is_connected(self) -> bool:
        return self.alive and not self.closed

    async def new_context(self, **_kw):
        ctx = _FakeContext()
        self.contexts.append(ctx)
        return ctx

    async def close(self) -> None:
        self.closed = True


class _FakeFirefoxType:
    def __init__(self) -> None:
        self.launched: list[_FakeBrowser] = []

    async def launch(self, **_kw):
        b = _FakeBrowser()
        self.launched.append(b)
        return b


async def _started(monkeypatch, recycle_after_n: int = 50):
    monkeypatch.setattr(
        browser_mod,
        "settings",
        browser_mod.settings.__class__(
            **{**browser_mod.settings.__dict__, "recycle_after_n": recycle_after_n}
        ),
    )
    ff = browser_mod.Firefox()
    fake = _FakeFirefoxType()
    ff._playwright = type("PW", (), {"firefox": fake})()
    await ff._ensure_current()
    return ff, fake


class TestFirefoxLifecycle:
    async def test_concurrent_jobs_share_one_firefox_fresh_context_each(self, monkeypatch) -> None:
        ff, fake = await _started(monkeypatch)
        async with ff.page():
            async with ff.page():
                assert len(fake.launched) == 1
                assert len(fake.launched[0].contexts) == 2
        assert all(c.closed for c in fake.launched[0].contexts)

    async def test_recycle_swaps_firefox_and_drains_old(self, monkeypatch) -> None:
        ff, fake = await _started(monkeypatch, recycle_after_n=2)
        async with ff.page():
            async with ff.page():  # 2nd job retires F1, but it is still in use
                async with ff.page():  # 3rd job gets a fresh F2
                    assert len(fake.launched) == 2
                    assert not fake.launched[0].closed
            assert not fake.launched[0].closed  # one job still on F1
        assert fake.launched[0].closed  # last F1 job done → closed
        assert not fake.launched[1].closed

    async def test_disconnected_firefox_is_relaunched(self, monkeypatch) -> None:
        ff, fake = await _started(monkeypatch)
        fake.launched[0].alive = False
        assert await ff.health_poke() is True
        assert len(fake.launched) == 2
        assert fake.launched[0].closed

    async def test_stop_closes_current_and_draining(self, monkeypatch) -> None:
        ff, fake = await _started(monkeypatch, recycle_after_n=1)
        cm = ff.page()
        await cm.__aenter__()  # F1 retired but busy
        await ff._ensure_current()  # F2 launched, F1 draining
        await ff.stop()
        assert all(b.closed for b in fake.launched)
