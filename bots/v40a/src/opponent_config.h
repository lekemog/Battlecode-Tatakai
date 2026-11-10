#pragma once
// 0 = compiled out; 1 = collect/log only; 2 = learned (default);
// 3 = fixed-pressure ablation, same observation/integration overhead.
#ifndef POLARIS_OPP_MODEL
#define POLARIS_OPP_MODEL 0
#endif
#if POLARIS_OPP_MODEL < 0 || POLARIS_OPP_MODEL > 3
#error POLARIS_OPP_MODEL must be 0, 1, 2 or 3
#endif
