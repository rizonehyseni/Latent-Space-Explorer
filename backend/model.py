import torch
from torch import nn


class MolecularVAE(nn.Module):
    def __init__(
        self,
        input_dim: int = 2048,
        hidden_dim: int = 512,
        latent_dim: int = 16,
    ) -> None:
        super().__init__()

        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 128),
            nn.ReLU(),
        )

        self.mu_layer = nn.Linear(128, latent_dim)
        self.log_var_layer = nn.Linear(128, latent_dim)

        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 128),
            nn.ReLU(),
            nn.Linear(128, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, input_dim),
        )

    def encode(self, fingerprints: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        hidden = self.encoder(fingerprints)
        return self.mu_layer(hidden), self.log_var_layer(hidden)

    def reparameterize(
        self,
        mu: torch.Tensor,
        log_var: torch.Tensor,
    ) -> torch.Tensor:
        standard_deviation = torch.exp(0.5 * log_var)
        noise = torch.randn_like(standard_deviation)
        return mu + noise * standard_deviation

    def decode(self, latent_vector: torch.Tensor) -> torch.Tensor:
        return self.decoder(latent_vector)

    def forward(
        self,
        fingerprints: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        mu, log_var = self.encode(fingerprints)
        latent_vector = self.reparameterize(mu, log_var)
        reconstruction_logits = self.decode(latent_vector)

        return reconstruction_logits, mu, log_var