#!/usr/bin/env python3
"""
Base class for emotion protocols in StillHere.

Emotion protocols are computational models that help understand and
process grief, loss, and other complex emotions through scientific
frameworks (quantum mechanics, thermodynamics, etc.).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class EmotionProtocol(ABC):
    """
    Abstract base class for all emotion protocols.

    Each protocol models a specific aspect of grief or loss using
    scientific/mathematical frameworks to provide understanding
    and validation for those experiencing profound loss.
    """

    # Protocol metadata (override in subclasses)
    id: str = "BaseProtocol.v0"
    name: str = "Base Emotion Protocol"

    @abstractmethod
    def simulate(self) -> Dict[str, Any]:
        """
        Run the core simulation/computation of the protocol.

        Returns:
            Dict containing simulation results. Structure depends
            on the specific protocol implementation.
        """
        pass

    @abstractmethod
    def plot(self, data: Dict[str, Any], save_path: Optional[str] = None,
             show: bool = True) -> None:
        """
        Visualize the protocol's results.

        Args:
            data: Simulation results from simulate()
            save_path: Optional path to save the visualization
            show: Whether to display the plot interactively
        """
        pass

    @abstractmethod
    def narrative(self) -> List[str]:
        """
        Return the human narrative that explains the science
        and connects it to the emotional experience.

        Returns:
            List of strings, each being a key insight or message.
        """
        pass

    def run(self, save_path: Optional[str] = None, show: bool = True) -> Dict[str, Any]:
        """
        Complete protocol execution: simulate, visualize, and narrate.

        Args:
            save_path: Optional path to save visualization
            show: Whether to display plots interactively

        Returns:
            Simulation results dictionary
        """
        print(f"\n=== {self.name} ({self.id}) ===\n")

        # Run simulation
        print("Running simulation...")
        data = self.simulate()

        # Generate visualization
        print("Generating visualization...")
        self.plot(data, save_path=save_path, show=show)

        # Share narrative
        print("\n=== Understanding ===")
        for line in self.narrative():
            print(f"  {line}")
        print()

        return data
