export type ErrorCode = 'validation_error' | 'not_found' | 'provider_error' | 'internal_error';

export class AppError extends Error {
  readonly code: ErrorCode;
  readonly status: number;
  readonly details: unknown;

  constructor(code: ErrorCode, message: string, status: number, details?: unknown) {
    super(message);
    this.name = 'AppError';
    this.code = code;
    this.status = status;
    this.details = details;
  }
}

export function notFound(what: string): AppError {
  return new AppError('not_found', `${what} not found`, 404);
}
