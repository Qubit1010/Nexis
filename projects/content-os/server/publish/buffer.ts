// Buffer GraphQL (api.buffer.com/graphql), Bearer BUFFER_API_KEY. Shapes verified
// by introspection 2026-10-21: createPost(input: CreatePostInput!) returns a
// PostActionPayload union (PostActionSuccess | *Error implementing MutationError);
// mode customScheduled + dueAt (ISO UTC) holds the post on Buffer's side, so it
// publishes even when this PC is off.
import { rootEnv } from "../config.ts";

const URL_ = "https://api.buffer.com/graphql";

export class BufferError extends Error {
  /** true when the request may have reached Buffer (a retry could duplicate the post). */
  ambiguous: boolean;
  constructor(message: string, ambiguous = false) {
    super(message);
    this.ambiguous = ambiguous;
  }
}

async function gql<T = any>(query: string, variables: Record<string, unknown> = {}): Promise<T> {
  const token = rootEnv().BUFFER_API_KEY;
  if (!token) throw new BufferError("BUFFER_API_KEY is not set in D:/Nexis/.env");
  let res: Response;
  try {
    res = await fetch(URL_, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({ query, variables }),
      signal: AbortSignal.timeout(45_000),
    });
  } catch (e) {
    // The request may or may not have arrived.
    throw new BufferError(`Buffer request failed: ${(e as Error).message}`, true);
  }
  const text = await res.text();
  let body: any;
  try {
    body = JSON.parse(text);
  } catch {
    throw new BufferError(`Buffer HTTP ${res.status}: ${text.slice(0, 200)}`, res.status >= 500);
  }
  if (res.status === 401 || body?.errors?.some((e: any) => e?.extensions?.code === "UNAUTHENTICATED")) {
    throw new BufferError("Buffer rejected the API key (Access token is not valid). Create a new key in Buffer and update BUFFER_API_KEY.");
  }
  if (body?.errors?.length) throw new BufferError(`Buffer error: ${JSON.stringify(body.errors).slice(0, 300)}`, res.status >= 500);
  return body.data as T;
}

export interface BufferChannel {
  id: string;
  service: string;
  displayName: string;
  type: string;
  isDisconnected: boolean;
}

export async function listChannels(): Promise<{ orgId: string; channels: BufferChannel[] }> {
  const acc = await gql<{ account: { organizations: { id: string }[] } }>("{ account { organizations { id } } }");
  const orgId = acc.account?.organizations?.[0]?.id;
  if (!orgId) throw new BufferError("no Buffer organization on this account");
  const data = await gql<{ channels: BufferChannel[] }>(
    "query($i:ChannelsInput!){ channels(input:$i){ id service displayName type isDisconnected } }",
    { i: { organizationId: orgId } },
  );
  return { orgId, channels: data.channels || [] };
}

export interface BufferPost {
  id: string;
  status: string; // draft | error | needs_approval | scheduled | sending | sent
  dueAt: string | null;
  sentAt: string | null;
  externalLink: string | null;
  error?: { message?: string } | null;
}

const POST_FIELDS = "id status dueAt sentAt externalLink error { message }";

export async function createScheduledPost(input: {
  channelId: string;
  text: string;
  dueAt: string;
  imageUrls?: string[];
  firstComment?: string;
}): Promise<BufferPost> {
  const variables = {
    input: {
      channelId: input.channelId,
      text: input.text,
      schedulingType: "automatic",
      mode: "customScheduled",
      dueAt: input.dueAt,
      needsApproval: false,
      assets: (input.imageUrls || []).map((url) => ({ image: { url } })),
      source: "content-os",
      ...(input.firstComment ? { metadata: { linkedin: { firstComment: input.firstComment } } } : {}),
    },
  };
  const data = await gql<{ createPost: any }>(
    `mutation($input: CreatePostInput!) { createPost(input: $input) {
      __typename
      ... on PostActionSuccess { post { ${POST_FIELDS} } }
      ... on MutationError { message }
    } }`,
    variables,
  );
  const r = data.createPost;
  if (r?.__typename !== "PostActionSuccess") throw new BufferError(`Buffer refused the post (${r?.__typename}): ${r?.message ?? "no message"}`);
  return r.post as BufferPost;
}

export async function getPost(id: string): Promise<BufferPost | null> {
  const data = await gql<{ post: BufferPost | null }>(`query($i: PostInput!) { post(input: $i) { ${POST_FIELDS} } }`, { i: { id } });
  return data.post;
}

export async function deletePost(id: string): Promise<void> {
  const data = await gql<{ deletePost: any }>(
    `mutation($i: DeletePostInput!) { deletePost(input: $i) { __typename ... on MutationError { message } } }`,
    { i: { id } },
  );
  if (data.deletePost?.__typename !== "DeletePostSuccess") throw new BufferError(`Buffer could not delete the post: ${data.deletePost?.message ?? data.deletePost?.__typename}`);
}

/** Posts on a channel due inside a window: used to settle an ambiguous createPost. */
export async function postsInWindow(orgId: string, channelId: string, startIso: string, endIso: string): Promise<(BufferPost & { text: string })[]> {
  const data = await gql<{ posts: { edges: { node: BufferPost & { text: string } }[] } }>(
    `query($i: PostsInput!) { posts(input: $i, first: 50) { edges { node { ${POST_FIELDS} text } } } }`,
    { i: { organizationId: orgId, filter: { channelIds: [channelId], dueAt: { start: startIso, end: endIso } } } },
  );
  return (data.posts?.edges || []).map((e) => e.node);
}
