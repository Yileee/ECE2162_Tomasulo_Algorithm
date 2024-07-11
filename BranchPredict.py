class BranchPredict:
    """
    A class representing a Branch Predictor for the Tomasulo algorithm.

    Attributes:
        btb (dict): A Branch Target Buffer (BTB) implemented as a dictionary.
                    The key is the branch instruction address, and the value is a tuple
                    containing the target address and the last taken decision.
        size (int): The maximum size of the BTB.
    """

    def __init__(self, size=8):
        """
        Initializes the BranchPredict class with an optional size for the BTB.

        Args:
            size (int): The maximum number of entries in the BTB. Default is 1024.
        """
        self.btb = {}
        self.size = size

    def predict(self, branch_addr):
        """
        Predicts whether a branch will be taken or not.

        Args:
            branch_addr (int): The address of the branch instruction.

        Returns:
            bool: True if the branch is predicted to be taken, False otherwise.
        """
        if branch_addr in self.btb:
            # Return the last known branch decision if the address is in the BTB
            return self.btb[branch_addr][1]
        else:
            # Default prediction is False (not taken) if the address is not in the BTB
            return False

    def update(self, branch_addr, target_addr, taken):
        """
        Updates the BTB with the new branch result.

        Args:
            branch_addr (int): The address of the branch instruction.
            target_addr (int): The target address of the branch.
            taken (bool): True if the branch was taken, False otherwise.
        """
        if len(self.btb) >= self.size:
            # If the BTB is full, remove the oldest entry
            self.btb.pop(next(iter(self.btb)))

        # Update the BTB with the new branch information
        self.btb[branch_addr] = (target_addr, taken)

def test():
    # Example usage
    bp = BranchPredict()
    branch_addr = 0x400000
    target_addr = 0x400004
    bp.update(branch_addr, target_addr, False)  # Update the BTB, assuming the branch is taken
    print(bp.predict(branch_addr))  # Predict if the branch will be taken


if __name__ == '__main__':
    test()