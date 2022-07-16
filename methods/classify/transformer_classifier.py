import matplotlib.pyplot as plt
import torch
from sklearn.metrics import (
    f1_score, accuracy_score,
    confusion_matrix
)
from sklearn.model_selection import train_test_split
from tqdm import tqdm
from transformers import (
    TrainingArguments, Trainer, pipeline,
    BertTokenizer, BertForSequenceClassification
)

from data_collection.utils import OTHERS, get_content
from methods.utils import WebDataset


class TransformerClassifier:
    _PATH = '../models'

    def __init__(
            self, data,
            load: bool = False,
            model_name: str = 'bert-base-cased',
            valtest_size: float = 0.2,
            test_size: float = 0.5,
            tokens_key: str = 'tokens'
    ):
        self.data = data
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.X, self.y, self.label2idx = self._getXy(tokens_key)
        self.X_train, self.X_testval, self.y_train, self.y_testval = train_test_split(
            self.X, self.y,
            test_size=valtest_size, random_state=1
        )
        self.X_val, self.X_test, self.y_val, self.y_test = train_test_split(
            self.X_testval, self.y_testval,
            test_size=test_size, random_state=1
        )
        self.tokenizer = self._get_tokenizer(model_name)
        encodings = self._get_encodings(self.tokenizer)
        self.datasets = self._get_datasets(*encodings)
        self.y_predicted = None
        self.model = self._get_model(model_name, load).to(self.device)
        self.generator = None

    @classmethod
    def _get_tokenizer(cls, model_name):
        return BertTokenizer.from_pretrained(model_name)

    def _get_model(self, model_name, load: bool):
        return BertForSequenceClassification.from_pretrained(
            model_name, num_labels=len(self.label2idx)
        ) if load else BertForSequenceClassification.from_pretrained(
            self._PATH
        )

    def _getXy(self, tokens_key: str):
        X = [get_content(doc[tokens_key]) for doc in self.data]
        y = [
            doc['category'] if doc['category'] else OTHERS
            for doc in self.data
        ]
        label2idx = {label: i for i, label in enumerate(list(set(y)))}
        y = [label2idx[label] for label in y]
        return X, y, label2idx

    def _get_encodings(self, tokenizer):
        train_encodings = tokenizer(self.X_train, truncation=True, padding=True)
        val_encodings = tokenizer(self.X_val, truncation=True, padding=True)
        test_encodings = tokenizer(self.X_test, truncation=True, padding=True)
        return train_encodings, val_encodings, test_encodings

    def _get_datasets(self, train_encodings, test_encodings, val_encodings):
        train_dataset = WebDataset(train_encodings, self.y_train)
        val_dataset = WebDataset(val_encodings, self.y_val)
        test_dataset = WebDataset(test_encodings, self.y_test)
        return train_dataset, val_dataset, test_dataset

    def _train(self, train_dataset, val_dataset):
        training_args = TrainingArguments(
            output_dir="./results",
            learning_rate=2e-5,
            per_device_train_batch_size=16,
            per_device_eval_batch_size=16,
            num_train_epochs=5,
            weight_decay=0.01,
            warmup_steps=500,
            logging_steps=10
        )

        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset
        )

        trainer.train()

    def _get_generator(self):
        return pipeline(
            'text-classification', self.model, tokenizer=self.tokenizer)

    def train(self):
        self._train(*self.datasets[:2])

    def test(self):
        y_predicted = []
        for x in tqdm(self.X_test):
            inp = self.tokenizer(
                x, truncation=True, padding=True, return_tensors='pt').to(self.device)
            output = self.model(**inp)
            y_predicted.append(output[0].softmax(1).argmax().item())
        self.y_predicted = y_predicted

    def save(self):
        self.model.save_pretrained(save_directory=self._PATH)

    def classify(self, x):
        inp = self.tokenizer(
            x, truncation=True, padding=True, return_tensors='pt').to(self.device)
        output = self.model(**inp)
        y_predicted = (output[0].softmax(1).argmax().item())
        return {v: k for k, v in self.label2idx}[y_predicted]

    def f1_score(self):
        return f1_score(self.y_test, self.y_predicted, average='macro')

    def accuracy(self):
        return accuracy_score(self.y_test, self.y_predicted)

    def confusion_matrix(self, plot: bool = False):
        matrix = confusion_matrix(
            self.y_test, self.y_predicted, labels=list(self.label2idx.keys()))
        if plot:
            plt.matshow(matrix)
            plt.colorbar()
            plt.ylabel('True label')
            plt.xlabel('Predicted label')
            plt.show()
