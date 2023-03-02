import torch
import torch.nn as nn

epsilon=1e-08
class HingeLoss(nn.Module):
	def __init__(self):
		super(HingeLoss, self).__init__()

	def forward_gen(self, input):
		# should be 1 or higher
		return (1-input).clamp(min=0) + epsilon

	def forward_real(self, input):
		# should be 1 higher
		return (1-input).clamp(min=0) + epsilon

	def forward_fake(self, input):
		# should be 0 or lower
		return input.clamp(min=0) + epsilon

@torch.jit.script
def _fw_ls_real(input):

	return (1-input).pow(2)

class LSLoss(nn.Module):
	def __init__(self):
		super(LSLoss, self).__init__()

	def forward_gen(self, input):
		# should be 1
		# return (1-input).pow(2)
		return _fw_ls_real(input) + epsilon

	def forward_real(self, input):
		# should be 1
		# return (1-input).pow(2)
		return _fw_ls_real(input) + epsilon

	def forward_fake(self, input):
		return input.pow(2) + epsilon


class NSLoss(nn.Module):
	def __init__(self):
		super(NSLoss, self).__init__()

	def forward_gen(self, input):
		# should be 1
		return torch.nn.functional.softplus(1-input+epsilon) + epsilon

	def forward_real(self, input):
		# should be 1
		return torch.nn.functional.softplus(1-input+epsilon) + epsilon

	def forward_fake(self, input):
		# should be 0
		return torch.nn.functional.softplus(input+epsilon) + epsilon
