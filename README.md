# Experiment 3: Analyze Synchronization Mechanisms in Parallel Programs

## Table of Contents
1. [Objective](#1-objective)
2. [Software Requirements](#2-software-requirements)
3. [Theory](#3-theory)
4. [Synchronization Mechanisms Diagram](#4-synchronization-mechanisms-diagram)
5. [Installation Steps (From Scratch)](#5-installation-steps-from-scratch)
6. [Programs and Compilation](#6-programs-and-compilation)
7. [Comparison Program (Scalability and Execution Time)](#7-comparison-program-scalability-and-execution-time)
8. [Execution Steps (Terminal)](#8-execution-steps-terminal)
9. [Results (From My Actual Runs)](#9-results-from-my-actual-runs)
10. [Analysis of Results](#10-analysis-of-results)
11. [Observation / Comparison Table](#11-observation--comparison-table)
12. [Conclusion](#12-conclusion)
13. [Repository Structure](#13-repository-structure)

---

## 1. Objective

To implement and study common synchronization mechanisms used in shared-memory parallel programs: an unsynchronized (race) update, critical sections, atomic operations, barriers, and semaphores/locks. The mechanisms are evaluated for **correctness**, **execution time**, and **scalability** as the number of threads increases.

---

## 2. Software Requirements

| S.No. | Software / Tool | Purpose |
|-------|-----------------|---------|
| 1 | VMware Workstation Pro | Virtualization software to host the Ubuntu guest OS |
| 2 | Ubuntu LTS (guest OS) | Guest operating system used for compiling and running the programs. **Used in this run: Ubuntu 24.04 LTS (Noble Numbat)**, as shown by the apt repositories in the screenshot. The lab sheet suggests 22.04 LTS, and the steps are identical on both. |
| 3 | GCC Compiler (build-essential) | Compiles the C programs. **Version used: gcc (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0** |
| 4 | OpenMP (libgomp, bundled with GCC) | Provides `#pragma omp` directives for parallel loops, critical, atomic, barrier |
| 5 | POSIX Threads (pthread) and Semaphore library | Used by the semaphore-based program |
| 6 | Ubuntu Terminal | Compile and execute all programs and record timing results |

---

## 3. Theory

### 3.1 Why Synchronization is Needed
In a shared-memory parallel program, multiple threads can read and write the same variable at the same time. If two threads perform a read-modify-write sequence (such as `counter++`) on a shared variable without coordination, their operations can interleave in a way that loses updates. This is called a **race condition**, and it produces results that depend unpredictably on thread scheduling. Synchronization mechanisms are language- and OS-level tools that control how threads access shared data so that the program's result stays correct regardless of scheduling.

### 3.2 Race Condition
A race condition occurs when the outcome of a program depends on the relative timing of multiple threads accessing shared data without protection. `counter++` is not a single CPU instruction. It is a read, an increment, and a write. If two threads read the same old value before either writes back the incremented value, one update is silently lost. Race conditions are fast (no synchronization overhead) but produce incorrect and non-repeatable results.

### 3.3 Critical Section
A critical section (`#pragma omp critical`) is a block of code that only one thread may execute at a time; all other threads attempting to enter must wait. It guarantees correctness by serializing access to the shared resource, but because every thread must queue up for the same lock, it becomes a scalability bottleneck as thread count grows. Performance can even get worse as more threads are added, since more time is spent waiting than working.

### 3.4 Atomic Operation
An atomic operation (`#pragma omp atomic`) tells the compiler to perform a simple read-modify-write (like `counter++`) using an indivisible, hardware-supported instruction (e.g., a CPU compare-and-swap or lock-add instruction) rather than a general-purpose lock. Because atomics use lightweight hardware support instead of OS-level mutex machinery, they are correct and typically scale much better than critical sections for simple updates. They only work for basic operations, not arbitrary code blocks.

### 3.5 Barrier
A barrier (`#pragma omp barrier`) is a synchronization point at which every thread must arrive before any thread is allowed to proceed. It does not protect shared data directly; instead it synchronizes the *phases* of a computation (e.g., ensuring all threads finish phase 1 before any thread starts phase 2). Barriers introduce waiting overhead equal to the time the slowest thread takes to reach the barrier.

### 3.6 Semaphore
A semaphore is a counter-based OS-level synchronization object. `sem_wait()` decrements the counter (blocking if it is already zero) and `sem_post()` increments it. A binary semaphore (initial value 1), as used in Program 5, behaves like a mutex lock, allowing only one thread into the protected region at a time. Semaphores are more general than mutexes (a counting semaphore can allow up to N threads into a region simultaneously) but that generality comes with moderate system-call overhead.

### 3.7 Correctness vs. Performance vs. Scalability
- **Correctness**: does it always produce the right answer regardless of scheduling?
- **Performance**: how fast does it run for a given number of threads?
- **Scalability**: does performance improve (or at least not degrade) as more threads are added?

An ideal mechanism is correct, fast, and scales well. In practice, stronger correctness guarantees usually cost more performance and scalability, which is exactly what this experiment measures.

---

## 4. Synchronization Mechanisms Diagram

```
 Thread 0 ─┐
 Thread 1 ─┤
 Thread 2 ─┼──►  [ Synchronization Mechanism ]  ──►  [ Shared Resource (counter) ]
 Thread 3 ─┘               │
        ┌──────────────────┼───────────────────┬──────────────────────┐
        ▼                  ▼                   ▼                      ▼
   None (Race)       Critical Section     Atomic Operation       Semaphore / Lock
   No protection;    Only one thread      Hardware-level         Counting/binary token
   threads overwrite executes the block   indivisible update,    controls access to the
   each other's      at a time (coarse    low overhead.          resource.
   updates.          lock).
```
*Fig. 1: Multiple threads accessing a shared resource through different synchronization mechanisms.*

---

## 5. Installation Steps (From Scratch)

### 5.1 Install VMware Workstation Pro
1. Download VMware Workstation Pro from the official Broadcom/VMware website for your host OS.
2. Run the installer and follow the setup wizard, accepting the license agreement.
3. Choose the installation location and finish the installation (enter a license key if prompted, or use the free version for personal use).
4. Launch VMware Workstation Pro once installation completes.

### 5.2 Create a New Virtual Machine
5. Open VMware Workstation and click **Create a New Virtual Machine**.
6. Select **Typical (recommended)** configuration and click Next.
7. Browse to the Ubuntu LTS ISO file (downloaded from ubuntu.com) as the installer disc image.
8. Enter a VM name and choose a storage location on the host disk.
9. Allocate disk space (20 GB or more recommended).
10. Under **Customize Hardware**, allocate at least 4 CPU cores and 2-4 GB RAM (multiple cores are needed to see real scalability differences).
11. Click **Finish** to create the VM.

### 5.3 Install Ubuntu
12. Power on the VM; it boots from the Ubuntu ISO.
13. Select **Install Ubuntu**, choose language and keyboard layout.
14. Choose **Erase disk and install Ubuntu** (this affects only the virtual disk).
15. Set time zone, create a username and password, and continue.
16. Restart the VM when installation finishes and remove the installation media.
17. Log in to the new Ubuntu desktop.

### 5.4 Install GCC and OpenMP
18. Open a Terminal (`Ctrl+Alt+T`) and update the package index:
    ```bash
    sudo apt update
    ```
19. Install `build-essential`, which provides GCC, G++, Make, and libgomp (the OpenMP runtime):
    ```bash
    sudo apt install build-essential -y
    ```
20. Verify GCC and OpenMP support:
    ```bash
    gcc --version
    echo '#include <omp.h>' | gcc -E -fopenmp -xc - > /dev/null && echo OpenMP OK
    ```

### 5.5 Environment Verification (Actual Output)

![GCC and OpenMP environment verification](screenshots/01-gcc-openmp-environment-verification.jpeg)

| Check | Observed Result |
|-------|-----------------|
| `sudo apt update` | All 4 repositories hit (`noble`, `noble-security`, `noble-updates`, `noble-backports`); **131 packages can be upgraded** |
| `sudo apt install build-essential -y` | `build-essential is already the newest version (12.10ubuntu1)`; 0 upgraded, 0 newly installed |
| `gcc --version` | `gcc (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0` |
| OpenMP check | Printed **`OpenMP OK`**, so OpenMP support is available |

---

## 6. Programs and Compilation

Each program demonstrates one synchronization approach for incrementing a shared counter (or, for the barrier program, synchronizing thread phases). All source files are in the [`source/`](source/) folder.

### 6.1 Program 1: Race Condition (No Synchronization) — `race.c`
```c
#include <stdio.h>
#include <omp.h>
int main(){
    long counter=0;
    #pragma omp parallel for
    for(long i=0;i<10000000;i++) counter++;
    printf("Counter=%ld\n",counter);
}
```
Compile: `gcc race.c -fopenmp -o race`

### 6.2 Program 2: Critical Section — `critical.c`
```c
#include <stdio.h>
#include <omp.h>
int main(){
    long counter=0;
    #pragma omp parallel for
    for(long i=0;i<10000000;i++){
        #pragma omp critical
        {counter++;}
    }
    printf("Counter=%ld\n",counter);
}
```
Compile: `gcc critical.c -fopenmp -o critical`

### 6.3 Program 3: Atomic Operation — `atomic.c`
```c
#include <stdio.h>
#include <omp.h>
int main(){
    long counter=0;
    #pragma omp parallel for
    for(long i=0;i<10000000;i++){
        #pragma omp atomic
        counter++;
    }
    printf("Counter=%ld\n",counter);
}
```
Compile: `gcc atomic.c -fopenmp -o atomic`

### 6.4 Program 4: Barrier — `barrier.c`
```c
#include <stdio.h>
#include <omp.h>
int main(){
    #pragma omp parallel
    {
        printf("Thread %d before barrier\n",omp_get_thread_num());
        #pragma omp barrier
        printf("Thread %d after barrier\n",omp_get_thread_num());
    }
}
```
Compile: `gcc barrier.c -fopenmp -o barrier`

### 6.5 Program 5: Semaphore — `semaphore.c`
```c
#include <stdio.h>
#include <pthread.h>
#include <semaphore.h>
sem_t semaphore;
int counter=0;
void* work(void* a){
    for(int i=0;i<100000;i++){
        sem_wait(&semaphore);
        counter++;
        sem_post(&semaphore);
    }
    return NULL;
}
int main(){
    pthread_t t1,t2;
    sem_init(&semaphore,0,1);
    pthread_create(&t1,NULL,work,NULL);
    pthread_create(&t2,NULL,work,NULL);
    pthread_join(t1,NULL);
    pthread_join(t2,NULL);
    printf("Counter=%d\n",counter);
    sem_destroy(&semaphore);
}
```
Compile: `gcc semaphore.c -pthread -o semaphore`

Two threads each increment 100,000 times, so the expected output is `Counter=200000`.

---

## 7. Comparison Program (Scalability and Execution Time)

Program 6 combines the **None, Critical, Atomic, and Lock** strategies into one benchmark. It repeats the same 10,000,000-increment workload for each mechanism across **1, 2, 4, and 8 threads** using `omp_set_num_threads()`, times every run with `omp_get_wtime()`, and checks the final counter value against the expected result. This program produces the data in Section 9. Full source: [`source/compare_sync.c`](source/compare_sync.c).

```c
/* compare_sync.c */
#include <stdio.h>
#include <omp.h>
#define N 10000000L

long run_none(int nthreads) {
    long counter = 0;
    omp_set_num_threads(nthreads);
    #pragma omp parallel for
    for (long i = 0; i < N; i++) {
        counter++;
    }
    return counter;
}

long run_critical(int nthreads) {
    long counter = 0;
    omp_set_num_threads(nthreads);
    #pragma omp parallel for
    for (long i = 0; i < N; i++) {
        #pragma omp critical
        {
            counter++;
        }
    }
    return counter;
}

long run_atomic(int nthreads) {
    long counter = 0;
    omp_set_num_threads(nthreads);
    #pragma omp parallel for
    for (long i = 0; i < N; i++) {
        #pragma omp atomic
        counter++;
    }
    return counter;
}

long run_lock(int nthreads) {
    long counter = 0;
    omp_lock_t lock; omp_init_lock(&lock);
    omp_set_num_threads(nthreads);
    #pragma omp parallel for
    for (long i = 0; i < N; i++) {
        omp_set_lock(&lock);
        counter++;
        omp_unset_lock(&lock);
    }
    omp_destroy_lock(&lock);
    return counter;
}

void run_and_report(const char *name, long (*fn)(int), int nthreads) {
    double start = omp_get_wtime();
    long result = fn(nthreads);
    double elapsed = omp_get_wtime() - start;
    const char *correctness = (result == N) ? "Correct" : "INCORRECT";
    printf("%-10s | %7d | %12ld | %10s | %10.4f\n",
           name, nthreads, result, correctness, elapsed);
}

int main(void) {
    int thread_counts[] = {1, 2, 4, 8};
    int num_configs = sizeof(thread_counts) / sizeof(thread_counts[0]);
    printf("Comparing synchronization mechanisms for %ld shared increments\n\n", N);
    printf("Mechanism | Threads | Final Count | Correctness | Time (s)\n");
    printf("---------------------------------------------------------------\n");
    for (int i = 0; i < num_configs; i++) {
        int t = thread_counts[i];
        run_and_report("None",     run_none,     t);
        run_and_report("Critical", run_critical, t);
        run_and_report("Atomic",   run_atomic,   t);
        run_and_report("Lock",     run_lock,     t);
        printf("---------------------------------------------------------------\n");
    }
    printf("\nExpected correct final count = %ld\n", N);
    printf("Observation: 'None' is fastest but incorrect (race condition).\n");
    printf("'Critical' is correct but slowest (coarse-grained locking).\n");
    printf("'Atomic' and 'Lock' are correct; 'Atomic' scales better since it\n");
    printf("uses lightweight hardware instructions instead of OS-level locks.\n");
    return 0;
}
```

Compile: `gcc compare_sync.c -fopenmp -o compare_sync`
Run: `./compare_sync`

---

## 8. Execution Steps (Terminal)

| Step | Command | Purpose |
|------|---------|---------|
| 1 | `sudo apt update && sudo apt install build-essential -y` | Install GCC, Make, and the OpenMP runtime |
| 2 | `nano race.c` (repeat for each `.c` file) | Create/paste each program's source code |
| 3 | `gcc race.c -fopenmp -o race` | Compile the race-condition program |
| 4 | `gcc critical.c -fopenmp -o critical` | Compile the critical-section program |
| 5 | `gcc atomic.c -fopenmp -o atomic` | Compile the atomic-operation program |
| 6 | `gcc barrier.c -fopenmp -o barrier` | Compile the barrier program |
| 7 | `gcc semaphore.c -pthread -o semaphore` | Compile the semaphore program |
| 8 | `gcc compare_sync.c -fopenmp -o compare_sync` | Compile the comparison/benchmark program |
| 9 | `OMP_NUM_THREADS=4 ./atomic` | Run any program with a chosen thread count |
| 10 | `./compare_sync` | Run the full comparison across 1/2/4/8 threads and record timings |

The thread count can also be set as an environment variable before running any OpenMP program:
```bash
export OMP_NUM_THREADS=8
./critical
```

---

## 9. Results (From My Actual Runs)

### 9.1 Benchmark Output: `./compare_sync` (Run 1, complete)

![Benchmark results](screenshots/02-sync-mechanisms-benchmark-results.jpeg)

```
master@master:~$ ./compare_sync
Comparing synchronization mechanisms for 10000000 shared increments

Mechanism  | Threads | Final Count | Correctness |   Time (s)
---------------------------------------------------------------
None       |       1 |    10000000 |    Correct |     0.0089
Critical   |       1 |    10000000 |    Correct |     0.1200
Atomic     |       1 |    10000000 |    Correct |     0.0678
Lock       |       1 |    10000000 |    Correct |     0.1131
---------------------------------------------------------------
None       |       2 |     8300185 |  INCORRECT |     0.0093
Critical   |       2 |    10000000 |    Correct |     0.2749
Atomic     |       2 |    10000000 |    Correct |     0.1037
Lock       |       2 |    10000000 |    Correct |     0.2632
---------------------------------------------------------------
None       |       4 |     7158836 |  INCORRECT |     0.0062
Critical   |       4 |    10000000 |    Correct |     0.3055
Atomic     |       4 |    10000000 |    Correct |     0.1041
Lock       |       4 |    10000000 |    Correct |     0.3068
---------------------------------------------------------------
None       |       8 |     3464896 |  INCORRECT |     0.0110
Critical   |       8 |    10000000 |    Correct |     0.2849
Atomic     |       8 |    10000000 |    Correct |     0.1126
Lock       |       8 |    10000000 |    Correct |     0.2982
---------------------------------------------------------------

Expected correct final count = 10000000
Observation: 'None' is fastest but incorrect (race condition).
'Critical' is correct but slowest (coarse-grained locking).
'Atomic' and 'Lock' are correct; 'Atomic' scales better since it
uses lightweight hardware instructions instead of OS-level locks.
```

#### Execution time summary (seconds, lower is better)

| Mechanism | 1 Thread | 2 Threads | 4 Threads | 8 Threads |
|-----------|---------:|----------:|----------:|----------:|
| None (race) | 0.0089 | 0.0093 | 0.0062 | 0.0110 |
| Critical | 0.1200 | 0.2749 | 0.3055 | 0.2849 |
| Atomic | 0.0678 | 0.1037 | 0.1041 | 0.1126 |
| Lock | 0.1131 | 0.2632 | 0.3068 | 0.2982 |

#### Correctness summary

| Mechanism | 1 Thread | 2 Threads | 4 Threads | 8 Threads |
|-----------|:--------:|:---------:|:---------:|:---------:|
| None (race) | Correct | INCORRECT (8,300,185) | INCORRECT (7,158,836) | INCORRECT (3,464,896) |
| Critical | Correct | Correct | Correct | Correct |
| Atomic | Correct | Correct | Correct | Correct |
| Lock | Correct | Correct | Correct | Correct |

#### Lost updates in the unsynchronized (race) version

| Threads | Final Count | Expected | Lost Updates | % of Updates Preserved |
|--------:|------------:|---------:|-------------:|-----------------------:|
| 1 | 10,000,000 | 10,000,000 | 0 | 100.0 % |
| 2 | 8,300,185 | 10,000,000 | 1,699,815 | 83.0 % |
| 4 | 7,158,836 | 10,000,000 | 2,841,164 | 71.6 % |
| 8 | 3,464,896 | 10,000,000 | 6,535,104 | 34.6 % |

### 9.2 Benchmark Output (Run 2, partial capture)

A second run of `./compare_sync` was performed on a different session (user `arun@master`, directory `~/Desktop`). The screenshot shows the tail end of that run (the 4-thread Atomic/Lock rows and the full 8-thread block):

![Barrier and benchmark tail](screenshots/03-barrier-synchronization-execution.jpeg)

| Mechanism | Threads | Final Count | Correctness | Time (s) |
|-----------|--------:|------------:|:-----------:|---------:|
| Atomic | 4 | 10000000 | Correct | 0.1325 |
| Lock | 4 | 10000000 | Correct | 0.6286 |
| None | 8 | 3727307 | INCORRECT | 0.0162 |
| Critical | 8 | 10000000 | Correct | 0.7792 |
| Atomic | 8 | 10000000 | Correct | 0.1319 |
| Lock | 8 | 10000000 | Correct | 0.7512 |

Note: this run was captured only in part, so the 1-thread, 2-thread and remaining 4-thread rows are not available. The same pattern holds: the race version loses 6,272,693 updates at 8 threads (final count 3,727,307), and Critical and Lock are about 5.7x slower than Atomic.

### 9.3 Barrier Program Output: `./barrier`

```
arun@master:~/Desktop$ ./barrier
Thread 0 before barrier
Thread 1 before barrier
Thread 3 before barrier
Thread 2 before barrier
Thread 1 after barrier
Thread 2 after barrier
Thread 0 after barrier
Thread 3 after barrier
```

**Observation:** All four threads (0 to 3) print their "before barrier" message first, in a non-deterministic arrival order (0, 1, 3, 2). Only after **all** four have arrived does any thread print "after barrier" (again in a non-deterministic order: 1, 2, 0, 3). No "after" line ever appears before the last "before" line, which confirms the barrier works as intended.

### 9.4 Other Programs (race.c, critical.c, atomic.c, semaphore.c)

No individual terminal screenshots were provided for these four stand-alone programs; their behaviour is covered by the `compare_sync` benchmark above (the None, Critical, Atomic and Lock rows). Expected outputs are:

| Program | Expected Output |
|---------|-----------------|
| `./race` | `Counter=<value less than 10000000>` (varies each run) |
| `./critical` | `Counter=10000000` |
| `./atomic` | `Counter=10000000` |
| `./semaphore` | `Counter=200000` |

---

## 10. Analysis of Results

Using Run 1 (complete data):

**1. Race condition (None).**
- With 1 thread the result is correct (10,000,000), since there is no concurrency.
- With 2, 4 and 8 threads the result is wrong every time and the damage grows with thread count: 1.70 M, 2.84 M and 6.54 M updates were lost respectively.
- At 8 threads, only about **35 %** of increments survived.
- It is the fastest variant, but the speed is meaningless because the answer is wrong.

**2. Critical section.**
- Always correct.
- Time rose from 0.1200 s (1 thread) to 0.2749 s (2 threads) and 0.3055 s (4 threads), then 0.2849 s (8 threads).
- Adding threads made it **slower**, not faster, because every iteration queues on the same lock. At 4 threads it is roughly **2.5x slower** than with 1 thread.

**3. Atomic operation.**
- Always correct.
- It is the fastest *correct* mechanism at every thread count: 0.0678, 0.1037, 0.1041, 0.1126 s.
- At 8 threads it is about **2.5x faster than Critical** (0.1126 s vs 0.2849 s) and about **2.6x faster than Lock** (0.1126 s vs 0.2982 s).
- Its time still rises slightly with threads, because all threads contend for one cache line holding the counter.

**4. Lock (`omp_lock_t`).**
- Always correct.
- Its timings (0.1131, 0.2632, 0.3068, 0.2982 s) closely track Critical, since both serialize all threads on a single lock.

**5. Barrier.**
- Produces no shared-data result. It only guarantees phase ordering, as seen in the output (Section 9.3).

**6. Scalability.**
- None of the correct mechanisms speeds up as threads are added in this benchmark. The workload is a single shared counter updated 10 million times, which is almost entirely serialized, so extra threads add contention rather than useful parallelism.
- Atomic degrades the least; Critical and Lock degrade the most.
- A real application would reduce contention differently (e.g., `reduction(+:counter)` with per-thread partial sums), which is outside this experiment.

**7. Comparison with the lab sheet's sample output.**
- The lab sheet's sample output (from another machine) shows correct results at 2 threads and flat timings across thread counts.
- My VM showed incorrect results already at 2 threads and rising timings. The sheet itself says values vary by machine, VM and core count; the qualitative trends (None incorrect, Atomic best among correct, Critical/Lock slowest) match.

---

## 11. Observation / Comparison Table

| Mechanism | Correctness | Relative Performance | Scalability |
|-----------|-------------|----------------------|-------------|
| None (race condition) | Incorrect | Fastest (no overhead) | Poor: wrong result gets worse with more threads |
| Critical section | Correct | Slowest (serializes all threads) | Poor: contention grows with thread count |
| Atomic operation | Correct | Fast (hardware-level) | Good: low overhead even as threads increase |
| Lock (`omp_lock_t`) | Correct | Slow (similar to critical) | Poor to Moderate |
| Barrier | Synchronization only | Waiting overhead | Moderate: limited by slowest thread |
| Semaphore | Correct | Moderate (system-call overhead) | Moderate |

---

## 12. Conclusion

Atomic operations provide the best balance of correctness and performance for simple shared-variable updates because they rely on lightweight hardware instructions. In my measurements, Atomic was correct at all thread counts and took about 0.11 s at 8 threads, versus about 0.28 s for Critical and 0.30 s for Lock. The unsynchronized version was the fastest but lost up to about 65 % of the updates at 8 threads (final count 3,464,896 instead of 10,000,000).

Critical sections and locks guarantee correctness but limit scalability since threads must wait in turn to enter the protected region. Barriers do not protect data but synchronize the phases of a parallel computation, at the cost of waiting for the slowest thread; the barrier run confirmed that every "after" line appeared only once all four threads had arrived. Semaphores generalize mutual exclusion (and can allow a controlled number of threads into a region) at a moderate overhead.

The benchmark confirms that unsynchronized access is fast but unreliable, while the choice among critical/atomic/lock/semaphore is a trade-off between strength of guarantee, overhead, and scalability as thread count grows.

---

## 13. Repository Structure

```
sync_experiment/
├── README.md
├── source/
│   ├── race.c
│   ├── critical.c
│   ├── atomic.c
│   ├── barrier.c
│   ├── semaphore.c
│   └── compare_sync.c
└── screenshots/
    ├── 01-gcc-openmp-environment-verification.jpeg
    ├── 02-sync-mechanisms-benchmark-results.jpeg
    └── 03-barrier-synchronization-execution.jpeg
```
