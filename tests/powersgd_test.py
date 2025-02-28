import pytest
import torch
import torchvision

from powersgd import PowerSGD, Config


@pytest.fixture
def model():
    return torchvision.models.resnet50(pretrained=True)


def test_no_compression_in_the_beginning(model):
    params = list(model.parameters())
    config = Config(
        rank=1,
        min_compression_rate=10,
        start_compressing_after_num_steps=2,
        num_iters_per_step=1,
    )
    powersgd = PowerSGD(list(params), config=config)
    gradients = [torch.randn_like(p) for p in params]
    grad_orig = [g.clone() for g in gradients]
    avg_grad = powersgd.aggregate(gradients)

    for grad in gradients:
        assert grad.allclose(torch.zeros_like(grad))

    for (grad, orig) in zip(avg_grad, grad_orig):
        assert grad.allclose(orig)

    assert powersgd.step_counter == 1


def test_error_feedback_mechanism(model):
    torch.set_default_dtype(torch.float64)
    model = torchvision.models.resnet50(pretrained=True)
    params = list(model.parameters())
    config = Config(
        rank=2,
        min_compression_rate=10,
        start_compressing_after_num_steps=0,
        num_iters_per_step=3,
    )
    powersgd = PowerSGD(list(params), config=config)

    gradients = [torch.randn_like(p) for p in params]

    grad_orig = [g.clone() for g in gradients]
    avg_grad = powersgd.aggregate(gradients)

    for orig, avg, buffer in zip(grad_orig, avg_grad, gradients):
        assert orig.allclose(avg + buffer)


if __name__ == "__main__":
    test_error_feedback_mechanism(model())
