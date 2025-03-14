from typing import List, Iterator, Dict, Tuple, Any, Type

import numpy as np
import torch
from copy import deepcopy

np.random.seed(1901)

class Attack:
    def __init__(
        self,
        vm, device, attack_path,
        min_val = 0,
        max_val = 1
    ):
        """
        args:
            vm: virtual model is wrapper used to get outputs/gradients of a model.
            device: system on which code is running "cpu"/"cuda"
            min_val: minimum value of each element in original image
            max_val: maximum value of each element in original image
                     each element in perturbed image should be in the range of min_val and max_val
            attack_path: Any other sources files that you may want to use like models should be available in ./submissions/ folder and loaded by attack.py. 
                         Server doesn't load any external files. Do submit those files along with attack.py
        """
        self.vm = vm
        self.device = device
        self.attack_path = attack_path
        self.min_val = 0
        self.max_val = 1
        self.eps = 0.006

    def attack(
        self, original_images: np.ndarray, labels: List[int], target_label = None,
    ):
        original_images = original_images.to(self.device)
        original_images = torch.unsqueeze(original_images, 0)
        labels = torch.tensor(labels).to(self.device)
        target_labels = target_label * torch.ones_like(labels).to(self.device)
        perturbed_image = original_images
        
        # -------------------- TODO ------------------ #

        # get gradient with repect to target labels
        for i in range(50):
          data_grad = self.vm.get_batch_input_gradient(original_images, target_labels)
          sign_data_grad = data_grad.sign()

        # perturb image
          perturbed_image = original_images - self.eps*sign_data_grad
          perturbed_image = torch.clamp(perturbed_image, self.min_val, self.max_val)

          original_images = perturbed_image
          original_images = original_images.detach()

          adv_outputs = self.vm.get_batch_output(perturbed_image)
          final_pred = adv_outputs.max(1, keepdim=True)[1]
          correct = 0
          correct += (final_pred == target_labels).sum().item()
          if(correct==1):
            break

        # ------------------ END TODO ---------------- #

        adv_outputs = self.vm.get_batch_output(perturbed_image)
        final_pred = adv_outputs.max(1, keepdim=True)[1]
        correct = 0
        correct += (final_pred == target_labels).sum().item()
        return np.squeeze(perturbed_image.cpu().detach().numpy()), correct