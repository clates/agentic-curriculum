/** The add-a-child limits. The server enforces the same ones (`AddChildRequest` and
 * `MAX_CHILDREN` in src/main.py) and answers 409 or 422. */
export const MAX_CHILDREN = 5;
/** Characters in a first name, and in each interest. */
export const MAX_TEXT_LENGTH = 40;
export const MAX_INTERESTS = 8;
export const MAX_NOTES_LENGTH = 500;
