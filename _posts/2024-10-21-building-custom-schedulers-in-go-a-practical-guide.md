---
title: "Building Custom Schedulers in Go: A Practical Guide"
layout: single

description: "Learn how to build efficient custom schedulers in Go with this practical guide, covering design patterns, concurrency best practices, and real-world implementation examples."
tags:
- concurrency
- custom
- design patterns
- go
- practical guide
- schedulers
---

## Introduction

Go, with its built-in concurrency model and lightweight goroutines, is a powerful language for building high-performance systems. While the Go runtime scheduler does an excellent job managing thousands — or even millions — of concurrent tasks, there are situations where you may want or need to take control of scheduling logic yourself. This is where *custom schedulers* come into play.

Custom schedulers are useful in scenarios where you want fine-grained control over which tasks run when, or where you need to optimize for specific behaviors such as fairness, task priorities, or resource constraints. In this article, we'll explore how to build custom schedulers in Go, when you might want to do so, and walk through a few practical examples.

## Why Use a Custom Scheduler?

The Go runtime scheduler is efficient and sophisticated, managing the execution of goroutines across available CPU threads. However, it operates at the system thread level, not the application logic level. There are cases where you need to control the scheduling of your application-level workloads separately from the runtime scheduler.

Common use cases for custom schedulers include:

- **Prioritization**: Handling high-priority tasks before lower ones.
- **Fairness**: Ensuring all clients or tasks get an equal share of processing time.
- **Rate Limiting or Throttling**: Restricting how many tasks are executed within a time window.
- **Workload Isolation**: Preventing one slow task from affecting the execution of others.
- **Specialized Queueing**: Using advanced queue structures like priority queues or job dependencies.

Using a custom scheduler doesn't replace the Go runtime scheduler, but sits on top of it to manage when and how your application-level tasks are executed.

## Basic Scheduler Design

At its core, a scheduler is responsible for:

1. **Receiving** tasks or jobs.
2. **Organizing** them (e.g., by priority or queue).
3. **Executing** them in a desired order or pattern.

Let's start by building a simple, custom scheduler using Go channels and goroutines.

```go
package main

import (
    "fmt"
    "sync"
)

type Job struct {
    ID   int
    Fn   func()
}

type Scheduler struct {
    jobQueue chan Job
    wg       sync.WaitGroup
}

func NewScheduler(workers int) *Scheduler {
    s := &Scheduler{
        jobQueue: make(chan Job),
    }

    s.wg.Add(workers)
    for i := 0; i < workers; i++ {
        go func() {
            defer s.wg.Done()
            for job := range s.jobQueue {
                job.Fn()
            }
        }()
    }

    return s
}

func (s *Scheduler) Submit(job Job) {
    s.jobQueue <- job
}

func (s *Scheduler) Shutdown() {
    close(s.jobQueue)
    s.wg.Wait()
}
```

In this example:

- The `Scheduler` maintains a queue of jobs.
- Multiple worker goroutines pull jobs from the queue and execute them.
- The `Submit` method sends a new job to the queue.
- `Shutdown` gracefully closes the queue and waits for workers to finish.

This is a starting point, but to make this scheduler useful for real-world applications, we need to add features like prioritization and fairness.

## Adding Priority with a Priority Queue

To support task prioritization, we can modify the scheduler to use a priority queue instead of a regular channel. Go doesn't have a built-in priority queue, but it's easy to build one using a heap.

```go
import (
    "container/heap"
)

type PriorityJob struct {
    priority int
    ID       int
    Fn       func()
}

// Priority Queue implementation
type PriorityQueue []PriorityJob

func (pq PriorityQueue) Len() int           { return len(pq) }
func (pq PriorityQueue) Less(i, j int) bool { return pq[i].priority > pq[j].priority }
func (pq PriorityQueue) Swap(i, j int)      { pq[i], pq[j] = pq[j], pq[i] }

func (pq *PriorityQueue) Push(x interface{}) {
    *pq = append(*pq, x.(PriorityJob))
}

func (pq *PriorityQueue) Pop() interface{} {
    old := *pq
    n := len(old)
    item := old[n-1]
    *pq = old[0 : n-1]
    return item
}

type PriorityScheduler struct {
    pq       PriorityQueue
    mutex    sync.Mutex
    workers  int
    shutdown bool
}

func (ps *PriorityScheduler) Submit(job PriorityJob) {
    ps.mutex.Lock()
    defer ps.mutex.Unlock()
    heap.Push(&ps.pq, job)
}

func (ps *PriorityScheduler) Run() {
    for i := 0; i < ps.workers; i++ {
        go func() {
            for !ps.shutdown {
                ps.mutex.Lock()
                if ps.pq.Len() > 0 {
                    job := heap.Pop(&ps.pq).(PriorityJob)
                    ps.mutex.Unlock()
                    job.Fn()
                } else {
                    ps.mutex.Unlock()
                    // Sleep or yield to prevent busy waiting
                }
            }
        }()
    }
}
```

This scheduler uses a heap-based data structure to ensure higher-priority jobs are executed first. However, managing access to the heap with locking can introduce contention. Alternative approaches, such as using a work-stealing queue or more advanced concurrency patterns, might be necessary depending on the workload characteristics.

## Fairness and Weighted Scheduling

One of the limitations of a priority-based scheduler is that low-priority jobs might be starved indefinitely if high-priority ones keep arriving. To address this, we can implement a *fair* or *weighted* scheduler.

A common pattern for fair scheduling