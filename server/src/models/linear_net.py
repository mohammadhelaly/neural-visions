import clip
import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from sklearn.metrics import average_precision_score


class LinearNet(nn.Module):
    def __init__(
        self,
        num_classes,
        model="ViT-L/14@336px",
        device=None,
        clip_download_directory=None,
    ):
        super().__init__()

        if device is None:
            device = torch.device("cpu")

        self.loss_train = []
        self.loss_val = []

        self.acc_vizwiz_train = []
        self.acc_vizwiz_val = []

        self.ans_train = []
        self.ans_val = []

        self.device = device
        self.model = model

        self.ans_loss_fn = nn.BCELoss()

        self.clip_model, self.preprocess = clip.load(
            model,
            device=device,
            download_root=clip_download_directory,
        )

        for param in self.clip_model.parameters():
            param.requires_grad = False

        self.fc1 = nn.Sequential(
            nn.LayerNorm(
                self.clip_model.visual.output_dim
                + self.clip_model.text_projection.shape[1]
            ),
            nn.Dropout(p=0.5),
            nn.Linear(
                self.clip_model.visual.output_dim
                + self.clip_model.text_projection.shape[1],
                512,
            ),
        )

        self.fc2 = nn.Sequential(
            nn.LayerNorm(512), nn.Dropout(p=0.5), nn.Linear(512, num_classes)
        )

        self.fc_aux = nn.Linear(512, 4)
        self.fc_gate = nn.Linear(4, num_classes)
        self.act_gate = nn.Sigmoid()

        self.fc_ans = nn.Sequential(
            nn.LayerNorm(
                self.clip_model.visual.output_dim
                + self.clip_model.text_projection.shape[1]
            ),
            nn.Linear(
                self.clip_model.visual.output_dim
                + self.clip_model.text_projection.shape[1],
                512,
            ),
        )

        self.fc_ans2 = nn.Linear(512, 1)
        self.ans_gate = nn.Sigmoid()

    def forward(self, image, question):

        image = torch.flatten(image, start_dim=1)
        question = torch.flatten(question, start_dim=1)
        x = torch.cat((image, question), dim=1)

        ans = self.fc_ans(x)
        ans = self.fc_ans2(ans)
        ans = self.ans_gate(ans)
        ans = ans.squeeze()

        x = self.fc1(x)

        aux = self.fc_aux(x)
        gate = self.fc_gate(aux)
        gate = self.act_gate(gate)

        vqa = self.fc2(x)
        output = vqa * gate

        return output, aux, ans

    def train_model(
        self, train_dataloader, val_dataloader, criterion, optimizer, num_epochs
    ):

        for epoch in range(0, num_epochs):
            train_loss, train_vizwiz_acc, train_ans = self.train_step(
                train_dataloader, criterion, optimizer, self.device
            )
            val_loss, val_vizwiz_acc, val_ans = self.val_step(
                val_dataloader, criterion, self.device
            )

            self.loss_train.append(train_loss)
            self.loss_val.append(val_loss)

            self.acc_vizwiz_train.append(train_vizwiz_acc)
            self.acc_vizwiz_val.append(val_vizwiz_acc)

            self.ans_train.append(train_ans)
            self.ans_val.append(val_ans)

            print(f"Epoch {epoch + 1}/{num_epochs}:")
            print(f"Training Loss: {train_loss:.4f} | Validation Loss: {val_loss:.4f}")
            print(
                f"Training Vizwiz Accuracy: {train_vizwiz_acc:.4f} | Validation Vizwiz Accuracy: {val_vizwiz_acc:.4f}"
            )
            print(
                f"Training Answerability Score: {train_ans:.4f} | Validation Answerability Score: {val_ans:.4f}"
            )
            print()

        return

    def train_step(self, dataloader, criterion, optimizer, device):

        training_loss, vizwiz_acc, sum = 0.0, 0.0, 0
        true_answerable = []
        predicted_answerable = []

        self.train()
        for _, batch in enumerate(dataloader):
            image, question, answer, answer_type, question_answers, answerable = batch
            image, question, answer, answer_type, question_answers, answerable = (
                image.to(device),
                question.to(device),
                answer.to(device),
                answer_type.to(device),
                question_answers.to(device),
                answerable.to(device),
            )
            optimizer.zero_grad()
            output, aux, ans = self.forward(image, question)

            answerable = 1 - answerable
            ans = 1.0 - ans

            loss = (
                criterion(output, answer)
                + criterion(aux, answer_type)
                + self.ans_loss_fn(ans, answerable)
            )
            loss.backward()
            optimizer.step()

            training_loss += loss.item()
            predicted_answer = torch.argmax(output, dim=1)

            for i in range(len(answer)):
                sum += 1
                vizwiz_acc += min(
                    1,
                    torch.sum(torch.eq(predicted_answer[i], question_answers[i])).item()
                    / 3,
                )
                true_answerable.append(answerable[i].item())
                predicted_answerable.append(ans[i].item())

        true_answerable = np.array(true_answerable)
        predicted_answerable = np.array(predicted_answerable)

        training_loss /= len(dataloader)
        vizwiz_acc /= sum

        return (
            training_loss,
            vizwiz_acc,
            average_precision_score(
                true_answerable, predicted_answerable, average="weighted"
            ),
        )

    def val_step(self, dataloader, criterion, device):

        val_loss, vizwiz_acc, sum = 0.0, 0.0, 0
        answerable_true = []
        answerable_predicted = []

        self.eval()
        with torch.no_grad():
            for _, batch in enumerate(dataloader):
                image, question, answer, answer_type, question_answers, answerable = (
                    batch
                )
                image, question, answer, answer_type, question_answers, answerable = (
                    image.to(device),
                    question.to(device),
                    answer.to(device),
                    answer_type.to(device),
                    question_answers.to(device),
                    answerable.to(device),
                )
                output, aux, ans = self.forward(image, question)

                answerable = 1 - answerable
                ans = 1.0 - ans
                loss = (
                    criterion(output, answer)
                    + criterion(aux, answer_type)
                    + self.ans_loss_fn(ans, answerable)
                )
                val_loss += loss.item()

                predicted_answer = torch.argmax(output, dim=1)

                for i in range(len(answer)):
                    if torch.sum(answer[i]) == 0:
                        continue
                    sum += 1

                    vizwiz_acc += min(
                        1,
                        torch.sum(
                            torch.eq(predicted_answer[i], question_answers[i])
                        ).item()
                        / 3,
                    )
                    answerable_true.append(answerable[i].item())
                    answerable_predicted.append(ans[i].item())

        answerable_true = np.array(answerable_true)
        answerable_predicted = np.array(answerable_predicted)

        val_loss /= len(dataloader)
        vizwiz_acc /= sum

        return (
            val_loss,
            vizwiz_acc,
            average_precision_score(
                answerable_true, answerable_predicted, average="weighted"
            ),
        )

    def test_step(self, dataloader):

        acc, sum, vizwiz_acc = 0.0, 0, 0.0
        answerable_true = []
        answerable_predicted = []

        self.eval()
        with torch.no_grad():
            for _, batch in enumerate(dataloader):
                image, question, answer, answer_type, question_answers, answerable = (
                    batch
                )
                image, question, answer, answer_type, question_answers, answerable = (
                    image.to(self.device),
                    question.to(self.device),
                    answer.to(self.device),
                    answer_type.to(self.device),
                    question_answers.to(self.device),
                    answerable.to(self.device),
                )
                output, _, ans = self.forward(image, question)

                answerable = 1 - answerable
                ans = 1.0 - ans

                predicted_answer = torch.argmax(output, dim=1)
                true_answer = torch.argmax(answer, dim=1)

                for i in range(len(answer)):
                    if torch.sum(answer[i]) == 0:
                        continue
                    if predicted_answer[i] == true_answer[i]:
                        acc += 1

                    vizwiz_acc += min(
                        1,
                        torch.sum(
                            torch.eq(predicted_answer[i], question_answers[i])
                        ).item()
                        / 3,
                    )
                    sum += 1

                    answerable_true.append(answerable[i].item())
                    answerable_predicted.append(ans[i].item())

        answerable_true = np.array(answerable_true)
        answerable_predicted = np.array(answerable_predicted)

        acc /= sum
        vizwiz_acc /= sum
        return (
            acc,
            vizwiz_acc,
            average_precision_score(
                answerable_true, answerable_predicted, average="weighted"
            ),
        )

    def predict(self, image, question):

        output, aux, ans = self.forward(image, question)
        ans = 1.0 - ans
        return output, aux, ans

    def test_model(self, image_path, question):

        self.eval()
        image = Image.open(image_path)

        image = self.preprocess(image).unsqueeze(0).to(self.device)
        image_features = self.clip_model.encode_image(image)
        image_features = torch.flatten(image_features, start_dim=1)

        question = clip.tokenize(question).to(self.device)
        text_features = self.clip_model.encode_text(question).float()
        text_features = torch.flatten(text_features, start_dim=1)

        predicted_answer, predicted_answer_type, predicted_answerability = self.predict(
            image_features, text_features
        )
        return predicted_answer, predicted_answer_type, predicted_answerability

    def plot_train_stats(self):

        plt.plot(self.loss_train, label="Training Loss")
        plt.plot(self.loss_val, label="Validation Loss")
        plt.legend()
        plt.show()

        plt.plot(self.acc_vizwiz_train, label="VizWiz Training Accuracy")
        plt.plot(self.acc_vizwiz_val, label="VizWiz Validation Accuracy")
        plt.legend()
        plt.show()

        plt.plot(self.ans_train, label="Training Answerability")
        plt.plot(self.ans_val, label="Validation Answerability")
        plt.legend()
        plt.show()

    def save_model(self, path):

        torch.save(self.state_dict(), path)

    def load_model(self, path):

        self.load_state_dict(
            torch.load(path, map_location=torch.device("cpu"), weights_only=True)
        )
        self.eval()
        return self
