import express from 'express';
import type { NextFunction, Request, Response } from 'express';

import { AppError } from './errors.ts';
import type { RouteContext } from './routes.ts';
import { createRoutes } from './routes.ts';

export function buildApp(ctx: RouteContext): express.Express {
  const app = express();

  app.disable('x-powered-by');
  app.use(express.json({ limit: '1mb' }));
  app.use('/api', createRoutes(ctx));

  app.use('/api', (_req: Request, res: Response) => {
    res.status(404).json({ error: { code: 'not_found', message: 'No such endpoint' } });
  });

  // Terminal error handler. Known failures get their contract shape; anything else is logged
  // in full server-side and reduced to a generic 500 on the wire, so internals never leak.
  app.use((error: unknown, _req: Request, res: Response, _next: NextFunction) => {
    if (error instanceof AppError) {
      res.status(error.status).json({
        error: { code: error.code, message: error.message, details: error.details },
      });
      return;
    }
    console.error('[replylab] unhandled error:', error);
    res.status(500).json({
      error: { code: 'internal_error', message: 'Something went wrong on the server.' },
    });
  });

  return app;
}
