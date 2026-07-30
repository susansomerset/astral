export const AST1017_PREAMBLE_CONFIG = {
  intro: "AST1017-INTRO: collect three source materials before Estelle.",
  validation_task_key: "preamble_validate_response",
  steps: [
    {
      id: "raw_resume",
      order: 1,
      prompt_1st_try: "AST1017-RESUME-1ST: paste your resume.",
      prompt_2nd_try: "AST1017-RESUME-2ND: paste resume again.",
      target: { blob: "context", field: "raw_resume" },
      validation_question: "valid resume?",
    },
    {
      id: "raw_profile",
      order: 2,
      prompt_1st_try: "AST1017-PROFILE-1ST: paste LinkedIn.",
      prompt_2nd_try: "AST1017-PROFILE-2ND: paste LinkedIn again.",
      target: { blob: "context", field: "raw_profile" },
      validation_question: "valid linkedin?",
    },
    {
      id: "raw_sample",
      order: 3,
      prompt_1st_try: "AST1017-SAMPLE-1ST: paste cover letter.",
      prompt_2nd_try: "AST1017-SAMPLE-2ND: paste cover again.",
      target: { blob: "context", field: "raw_sample" },
      validation_question: "valid cover?",
    },
  ],
} as const
