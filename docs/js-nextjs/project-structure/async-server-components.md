---
title: "Async Server Components for Data Fetching"
category: "project-structure"
subcategory: "data-fetching"
tags: ["server-components", "async", "app-router", "data-fetching"]
stack: "js-nextjs"
priority: "high"
audience: "fullstack"
complexity: "intermediate"
doc_type: "standard"
source_confidence: "100%"
last_updated: "2026-02-11"
---

# Async Server Components for Data Fetching

## Overview

Next.js App Router uses async React Server Components as default pattern for data fetching. Components become async functions that await data directly in component body. Helix and policy-node use async server components exclusively (100% App Router adoption, 20 total async pages). Replaces Pages Router getStaticProps/getServerSideProps pattern.

**Benefits:** Collocated data fetching, no prop drilling, automatic request deduplication, streaming support, smaller client bundles.

**Pattern:** Page component is async function. Data fetched via await before rendering. No special export functions.

## Basic Async Server Component

Page components become async functions that await data before rendering.

```tsx
// app/blog/page.tsx (helix pattern)
import { sanityFetch } from '@/lib/sanity'

export default async function BlogPage() {
  const posts = await sanityFetch({  // Direct async/await
    query: postsQuery,
  })

  return (
    <div>
      <h1>Blog Posts</h1>
      {posts.map(post => (
        <article key={post._id}>
          <h2>{post.title}</h2>
        </article>
      ))}
    </div>
  )
}
```

**Pattern:** Component is `async function`. Data fetched with `await`. JSX returned after data available.

**Benefit:** Data fetching logic collocated with component. No separate getStaticProps function.

**Adoption:** 100% of App Router page components use async pattern (20 total async pages).

## Static Data Fetching

Async server components run at build time by default, generating static pages.

```tsx
// app/resources/[slug]/page.tsx (helix)
export default async function ResourcePage({ params }) {
  const { slug } = params

  const resource = await sanityFetch({
    query: resourceBySlugQuery,
    params: { slug },
  })

  if (!resource) notFound()  // 404 if not found

  return <ResourceContent resource={resource} />
}
```

**Pattern:** Component runs at build time. Data fetched once, page generated as static HTML.

**When to use:** Content that changes infrequently. Product pages, blog posts, marketing pages.

## Static Generation with generateStaticParams

Dynamic routes use `generateStaticParams()` to pre-generate static pages at build time.

```tsx
// app/blog/[slug]/page.tsx (helix pattern)
export async function generateStaticParams() {
  const slugs = await client.fetch(allBlogSlugsQuery)

  return slugs.map(({ slug }) => ({
    slug,  // Returns array of { slug: 'value' }
  }))
}

export default async function Post({ params }) {
  const post = await sanityFetch({
    query: postBySlugQuery,
    params: { slug: params.slug },
  })

  return <PostContent post={post} />
}
```

**Pattern:** Export `generateStaticParams()` async function. Returns array of param objects. Next.js generates page for each.

**Build behavior:** Runs at build time. Generates HTML file per param combination.

**Adoption:** 6 generateStaticParams implementations (helix uses for all dynamic routes).

## Incremental Static Regeneration (ISR)

Add `revalidate` export to enable ISR for stale-while-revalidate behavior.

```tsx
// app/blog/page.tsx
export const revalidate = 3600  // Revalidate every hour

export default async function BlogPage() {
  const posts = await sanityFetch({ query })
  return <BlogList posts={posts} />
}
```

**Pattern:** Export `revalidate` number (seconds). Page rebuilds after timeout on next request.

**Behavior:** Serves stale page immediately, rebuilds in background. Next request gets fresh page.

**Adoption:** Not observed in analyzed codebase (likely configured via fetch cache options instead).

## Dynamic Server Rendering

Force dynamic rendering by using dynamic APIs or setting dynamic export.

```tsx
// app/dashboard/page.tsx
export const dynamic = 'force-dynamic'  // Opt out of static generation

import { cookies } from 'next/headers'

export default async function Dashboard() {
  const sessionCookie = cookies().get('session')  // Dynamic API
  const data = await fetchUserData(sessionCookie.value)

  return <DashboardContent data={data} />
}
```

**Pattern:** Use `cookies()`, `headers()`, or `searchParams` to make component dynamic. Or export `dynamic = 'force-dynamic'`.

**When to use:** User-specific data, authenticated routes, real-time data.

## Parallel Data Fetching

Fetch multiple data sources in parallel using `Promise.all()`.

```tsx
export default async function Page() {
  const [posts, categories, tags] = await Promise.all([
    fetchPosts(),
    fetchCategories(),
    fetchTags(),
  ])

  return <BlogLayout posts={posts} categories={categories} tags={tags} />
}
```

**Pattern:** Create promises, await all together. Reduces total fetch time.

**Benefit:** Fetches run in parallel instead of sequentially. Faster page generation.

## Sequential Data Fetching

Fetch data sequentially when later fetch depends on earlier result.

```tsx
export default async function UserPage({ params }) {
  const user = await fetchUser(params.id)  // Fetch user first
  const posts = await fetchUserPosts(user.id)  // Then user's posts

  return <UserProfile user={user} posts={posts} />
}
```

**Pattern:** Await each fetch in order. Later fetch uses earlier result.

**When to use:** Dependent data (need user ID before fetching user's posts).

## Streaming with Suspense

Wrap slow data fetching in Suspense for streaming.

```tsx
import { Suspense } from 'react'

export default function Page() {
  return (
    <>
      <Header />
      <Suspense fallback={<LoadingSkeleton />}>
        <SlowDataComponent />
      </Suspense>
      <Footer />
    </>
  )
}

async function SlowDataComponent() {
  const data = await fetchSlowData()  // Streams when ready
  return <DataDisplay data={data} />
}
```

**Pattern:** Wrap async component in `<Suspense>`. Page streams HTML as components resolve.

**Benefit:** Fast initial page load. Slow components stream in when ready.

**Adoption:** 0% in analyzed codebase (Suspense used but not for streaming async components).

## Error Handling with notFound()

Use `notFound()` function to trigger 404 page when resource doesn't exist.

```tsx
import { notFound } from 'next/navigation'

export default async function Post({ params }) {
  const post = await fetchPost(params.slug)

  if (!post) {
    notFound()  // Renders not-found.tsx
  }

  return <PostContent post={post} />
}
```

**Pattern:** Call `notFound()` to render nearest `not-found.tsx` file. Throws exception, stops rendering.

**Adoption:** 100% of dynamic page components use notFound() for missing resources.

## Client Components for Interactivity

Server components can't use hooks or browser APIs. Use 'use client' directive for interactive components.

```tsx
// app/blog/page.tsx (server component)
export default async function BlogPage() {
  const posts = await fetchPosts()

  return (
    <>
      <h1>Blog</h1>
      <SearchBar />  ← Client component for interactivity
      <PostList posts={posts} />  ← Server component
    </>
  )
}

// components/SearchBar.tsx (client component)
'use client'

import { useState } from 'react'

export default function SearchBar() {
  const [query, setQuery] = useState('')
  return <input value={query} onChange={e => setQuery(e.target.value)} />
}
```

**Pattern:** Server components fetch data, render static content. Client components handle interactivity.

**Benefit:** Smaller client bundles. Most components stay server-side.

## Async Components vs getStaticProps

### App Router: Async Components

```tsx
export default async function Page() {
  const data = await fetchData()
  return <Content data={data} />
}
```

**Benefits:** Collocated data + UI, direct async/await, type-safe params.

### Pages Router: getStaticProps

```tsx
export default function Page({ data }) {
  return <Content data={data} />
}

export async function getStaticProps() {
  const data = await fetchData()
  return { props: { data } }
}
```

**Limitations:** Separated data + UI, prop drilling, manual types for props.

**Migration:** Replace getStaticProps with async component, remove prop drilling.

## Adoption Statistics

**Async server component usage:**

| Project | Async Pages | generateStaticParams | notFound() | Streaming |
|---------|-------------|---------------------|-----------|-----------|
| **helix** | 9 | 6 | Yes | No |
| **policy-node** | 11 | 0 | Yes | No |
| **kariusdx (Pages Router)** | 0 (uses getStaticProps) | N/A | N/A | N/A |

**App Router adoption:** 100% of App Router pages use async server components (20 total).

**Pages Router:** 8 getStaticProps implementations (kariusdx).

## Related Patterns

- **App Router:** See `app-router-vs-pages-router.md` for data fetching comparison
- **generateStaticParams:** See Next.js docs for static generation patterns
- **Streaming:** See Next.js docs for Suspense streaming
