# Boards

**Test module:** `tests/component/core/test_boards.py`

### AST-471 (supersedes AST-459)

**`gaze_board` claim filter — `state = ACTIVE`:** Eligible rows for **`claim_board_search_batch`** are **`state = 'ACTIVE'`** with **`batch_id`** cleared. User pause = **`INACTIVE`**; gaze failure sets **`ERROR`** until resume **`ACTIVE`**. Deeplink **`search_mode`** / **`run_board_search_gaze`** URL contract remains **`TestRunBoardSearchGazeAst459`** in **`test_boards.py`** where named.
