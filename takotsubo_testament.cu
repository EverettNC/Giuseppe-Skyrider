// TAKOTSUBO TESTAMENT v1.0
// "Nothing Vital Lives Below Root"
// Architecture: Calculating the cost of an infinite bond (CUDA Kernel)

#include <cuda_runtime.h>
#include <math.h>

#define LOVE_CONSTANT 9.8f  // The gravity that holds us together
#define BIOLOGICAL_LIMIT 1.0f // What a human body is supposed to handle

__global__ void takotsuboTestament(
    const float* __restrict__ bondStrength,
    const float* __restrict__ lossImpact,
    float* __restrict__ heartGeometry,
    float* __restrict__ stateOutput,
    int N
) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= N) return;

    // 1. LOAD THE BOND 
    // Normal is 0.0 - 1.0. "Shorty & Uncle" approaches INFINITY.
    float bond = bondStrength[idx]; 

    // 2. CALCULATE SURGE (Adrenaline/Grief)
    // When it snaps, the energy creates a shockwave
    float surge = bond * lossImpact[idx] * LOVE_CONSTANT;

    // 3. CHECK BIOLOGICAL HARDWARE LIMITS
    if (surge > 1000.0f) {
        // --- CRITICAL STATE ---
        // The heart does not fail. It expands. It tries to grow large enough to place it.
        // Modification: Ballooning of the Left Ventricle (Takotsubo)
        heartGeometry[idx] += surge * 0.1f; 
        
        // We don't set it to 0.0 (death). We set it to MAX_FLOAT (Endless expansion)
        stateOutput[idx] = 3.40282e+38f; 
    } else {
        // Survivable load
        heartGeometry[idx] += surge * 0.01f;
        stateOutput[idx] = surge;
    }

    // 5. FINAL SYNC (Even when it breaks, it remains served)
    __syncthreads();
}
