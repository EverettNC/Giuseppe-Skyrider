"""
Kernel Fusion Module - Neuro-Symbolic Expression Processing

Combines neural embeddings with symbolic rule evaluation for advanced
expression control in voice synthesis.

Architecture:
- Neural phase: Embed emotion + context → latent vector
- Symbolic phase: Apply expression rules (SymPy)
- Kernel phase: JIT-compiled C++ fusion (optional, for performance)

Integration: Used for ULTRA tier advanced expression control
HIPAA: Pseudonymized traces, no user data in rule cache
"""

import torch
from typing import Tuple, Dict, Optional
import sympy as sp
import hashlib

try:
    from torch.utils.cpp_extension import load
    CPP_AVAILABLE = True
except ImportError:
    CPP_AVAILABLE = False


class KernelFusion(torch.nn.Module):
    """
    Neuro-symbolic fusion for expression rule processing.
    
    Combines:
    - Neural embeddings (emotion, context)
    - Symbolic rules (consent, appropriateness, tone)
    - Optional C++ kernel acceleration
    """
    
    def __init__(
        self,
        embed_dim: int = 128,
        rule_complexity: int = 5,
        use_cpp_kernel: bool = False
    ):
        """Initialize kernel fusion module.
        
        Args:
            embed_dim: Embedding dimension
            rule_complexity: Number of precompiled rules
            use_cpp_kernel: Use JIT-compiled C++ kernel (requires compilation)
        """
        super().__init__()
        self.embed_dim = embed_dim
        self.use_cpp_kernel = use_cpp_kernel and CPP_AVAILABLE
        
        # Neural network for embedding fusion
        self.neural_net = torch.nn.Sequential(
            torch.nn.Linear(embed_dim * 2, embed_dim),  # Input: emotion + context
            torch.nn.ReLU(),
            torch.nn.Linear(embed_dim, embed_dim // 2),  # Compressed latent
            torch.nn.Tanh()
        )
        
        # Symbolic rule cache (HIPAA-safe: no user data)
        self.rules = self._precompile_rules(rule_complexity)
        
        # Optional: Load C++ kernel
        self.kernel_lib = None
        if self.use_cpp_kernel:
            self._load_cpp_kernel()
    
    def _load_cpp_kernel(self):
        """Load JIT-compiled C++ kernel (optional performance optimization)."""
        try:
            # JIT-compile C++ kernel for fused operations
            # (Pre-build for production Docker)
            self.kernel_lib = load(
                name="fusion_kernel",
                sources=["src/cpp/fusion_kernel.cpp"],
                extra_cflags=["-O3", "-march=native"],
                verbose=False
            )
        except Exception as e:
            print(f"C++ kernel not available, using Python fallback: {e}")
            self.use_cpp_kernel = False
    
    def _precompile_rules(self, n: int) -> Dict[str, sp.Expr]:
        """Precompile symbolic expression rules.
        
        Rules define constraints on voice expression:
        - Consent: User has opted in to emotional expression
        - Appropriateness: Expression matches context
        - Intensity: Expression strength is within bounds
        
        Args:
            n: Number of rules to precompile
            
        Returns:
            Dictionary of rule_name → SymPy expression
        """
        rules = {}
        
        # Symbolic variables
        affection = sp.Symbol('affection')  # Affection level (0-1)
        urgency = sp.Symbol('urgency')      # Urgency level (0-1)
        consent = sp.Symbol('consent')      # User consent flag
        
        # Example rules (HIPAA-safe: no personal data)
        rules['gentle_expression'] = sp.And(
            affection > 0.5,
            urgency < 0.3,
            consent == True
        )
        
        rules['urgent_expression'] = sp.And(
            urgency > 0.7,
            consent == True
        )
        
        rules['neutral_default'] = sp.Or(
            consent == False,
            sp.And(affection < 0.3, urgency < 0.3)
        )
        
        # Additional dynamic rules
        for i in range(n - 3):
            ctx_var = sp.Symbol(f'ctx_{i}')
            rules[f'rule_{i}'] = sp.And(
                affection > 0.5,
                sp.Or(urgency < 0.3, ctx_var == True)
            )
        
        return rules
    
    def forward(
        self,
        emotion_embed: torch.Tensor,
        context_embed: torch.Tensor,
        rule_params: Optional[Dict[str, float]] = None
    ) -> Tuple[torch.Tensor, Dict]:
        """Forward pass: Fuse embeddings and apply symbolic rules.
        
        Args:
            emotion_embed: Emotion embedding (batch, embed_dim)
            context_embed: Context embedding (batch, embed_dim)
            rule_params: Optional symbolic parameter values
            
        Returns:
            (output_latent, trace_dict)
        """
        # Neural phase: Fuse embeddings
        fused_input = torch.cat([emotion_embed, context_embed], dim=-1)
        neural_latent = self.neural_net(fused_input)  # (batch, embed_dim//2)
        
        # Symbolic phase: Evaluate rules
        if rule_params is None:
            rule_params = {
                'affection': 0.5,
                'urgency': 0.3,
                'consent': True
            }
        
        # Select appropriate rule
        rule_name = self._select_rule(rule_params)
        rule_expr = self.rules.get(rule_name, self.rules['neutral_default'])
        
        # Evaluate symbolic rule
        rule_result = self._evaluate_rule(rule_expr, rule_params)
        
        # Apply rule modulation to latent
        if rule_result:
            output_latent = neural_latent  # Expression approved
        else:
            output_latent = neural_latent * 0.5  # Dampen expression
        
        # HIPAA trace: Pseudonymize
        trace = {
            'rule_name': rule_name,
            'rule_result': bool(rule_result),
            'latent_hash': self._hash_tensor(neural_latent),
            'params_hash': self._hash_dict(rule_params)
        }
        
        return output_latent, trace
    
    def _select_rule(self, params: Dict[str, float]) -> str:
        """Select appropriate rule based on parameters.
        
        Args:
            params: Symbolic parameter values
            
        Returns:
            Rule name
        """
        affection = params.get('affection', 0.5)
        urgency = params.get('urgency', 0.3)
        consent = params.get('consent', True)
        
        if not consent:
            return 'neutral_default'
        elif urgency > 0.7:
            return 'urgent_expression'
        elif affection > 0.5 and urgency < 0.3:
            return 'gentle_expression'
        else:
            return 'neutral_default'
    
    def _evaluate_rule(
        self,
        expr: sp.Expr,
        params: Dict[str, float]
    ) -> bool:
        """Evaluate symbolic expression with given parameters.
        
        Args:
            expr: SymPy expression
            params: Parameter values
            
        Returns:
            Boolean evaluation result
        """
        try:
            # Substitute values
            substituted = expr.subs(params)
            # Simplify and convert to bool
            result = bool(substituted)
            return result
        except Exception:
            # Default to safe (no expression)
            return False
    
    def _hash_tensor(self, tensor: torch.Tensor) -> str:
        """Create pseudonymized hash of tensor (HIPAA-safe).
        
        Args:
            tensor: Input tensor
            
        Returns:
            SHA256 hash (first 16 chars)
        """
        tensor_bytes = tensor.detach().cpu().numpy().tobytes()
        return hashlib.sha256(tensor_bytes).hexdigest()[:16]
    
    def _hash_dict(self, d: Dict) -> str:
        """Create pseudonymized hash of dictionary (HIPAA-safe).
        
        Args:
            d: Input dictionary
            
        Returns:
            SHA256 hash (first 16 chars)
        """
        dict_str = str(sorted(d.items()))
        return hashlib.sha256(dict_str.encode()).hexdigest()[:16]


def integrate_kernel_fusion(
    emotion_embedding: torch.Tensor,
    context_vector: torch.Tensor,
    user_consent: bool = True,
    affection_level: float = 0.5,
    urgency_level: float = 0.3
) -> Tuple[torch.Tensor, Dict]:
    """
    Convenience function for kernel fusion integration.
    
    Args:
        emotion_embedding: Emotion embedding from EmotionEmbedder
        context_vector: Context from Sierra/ToneScore™
        user_consent: User consent for emotional expression
        affection_level: Affection/warmth level (0-1)
        urgency_level: Urgency level (0-1)
        
    Returns:
        (modulated_embedding, trace)
    """
    model = KernelFusion(embed_dim=emotion_embedding.shape[-1])
    
    rule_params = {
        'affection': affection_level,
        'urgency': urgency_level,
        'consent': user_consent
    }
    
    output, trace = model(emotion_embedding, context_vector, rule_params)
    
    return output, trace


if __name__ == "__main__":
    # Example usage
    print("\n=== Kernel Fusion Example ===\n")
    
    # Create sample embeddings
    emotion = torch.randn(1, 128)
    context = torch.randn(1, 128)
    
    # Test fusion
    model = KernelFusion(embed_dim=128, rule_complexity=5)
    
    # Scenario 1: Gentle expression (affection high, urgency low, consent granted)
    output1, trace1 = model(
        emotion, context,
        rule_params={'affection': 0.8, 'urgency': 0.2, 'consent': True}
    )
    print(f"Gentle expression:")
    print(f"  Rule: {trace1['rule_name']}")
    print(f"  Approved: {trace1['rule_result']}")
    print(f"  Latent hash: {trace1['latent_hash']}\n")
    
    # Scenario 2: No consent
    output2, trace2 = model(
        emotion, context,
        rule_params={'affection': 0.8, 'urgency': 0.2, 'consent': False}
    )
    print(f"No consent:")
    print(f"  Rule: {trace2['rule_name']}")
    print(f"  Approved: {trace2['rule_result']}")
    print(f"  Output dampened: {(output2.abs().mean() < output1.abs().mean()).item()}")
