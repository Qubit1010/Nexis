import { z } from 'zod';

export const createEnquirySchema = z.object({
  subject: z.string().trim().min(1, 'Subject is required').max(300),
  body: z.string().trim().min(1, 'Body is required').max(20_000),
});

export const updateDraftSchema = z
  .object({
    editedText: z.string().max(50_000).optional(),
    rating: z.union([z.literal('good'), z.literal('bad'), z.null()]).optional(),
  })
  .refine((value) => value.editedText !== undefined || value.rating !== undefined, {
    message: 'Provide at least one of editedText or rating',
  });

export const createPromptSchema = z.object({
  systemPrompt: z.string().trim().min(1, 'The prompt cannot be empty').max(20_000),
  label: z.string().trim().min(1).max(120).optional(),
});

export const idParamSchema = z.coerce.number().int().positive();
