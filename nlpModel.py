import torch
from torch import nn


class TextClassificationModel(nn.Module):
    def __init__(self, vocab_size, embed_dim, num_class):
        super(TextClassificationModel, self).__init__()
        self.embedding = nn.EmbeddingBag(vocab_size, embed_dim, sparse=True)
        self.fc = nn.Linear(embed_dim, num_class)
        self.init_weights()

    def init_weights(self):
        initrange = 0.5
        self.embedding.weight.data.uniform_(-initrange, initrange)
        self.fc.weight.data.uniform_(-initrange, initrange)
        self.fc.bias.data.zero_()

    def forward(self, text, offsets):
        embedded = self.embedding(text, offsets)
        return self.fc(embedded)


class BasicGRU(nn.Module):
    def __init__(self,
                 vocab_size,
                 batch_size,
                 embedding_dimension,
                 hidden_size,
                 n_layers,
                 device,
                 n_classes
                 ):
        super(BasicGRU, self).__init__()
        self.n_layer = n_layers
        self.hidden_size = hidden_size
        self.device = device
        self.batch_size = batch_size

        self.encoder = nn.EmbeddingBag(vocab_size, embedding_dimension)
        self.gru = nn.GRU(embedding_dimension, hidden_size,
                          num_layers=n_layers,
                          batch_first=True)
        self.Linear = nn.Linear(hidden_size, n_classes)

    def init_hidden(self):
        return torch.randn(self.n_layer, self.batch_size, self.hidden_size).to(self.device)

    def forward(self, input, offsets):
        batch_size = input.size(0)
        if batch_size != self.batch_size:
            self.batch_size = batch_size

        encoded = self.encoder(input, offsets)
        print(encoded)
        print(encoded.shape)
        exit()
        output, hidden = self.gru(encoded, self.init_hidden())
        output = self.Linear(output[:, :, -1]).squeeze()
        return output
