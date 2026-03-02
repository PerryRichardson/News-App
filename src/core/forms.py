from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Article, Publisher, User


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ["title", "body", "publisher"]

class PublisherForm(forms.ModelForm):
    """
    Form for creating a Publisher through the web UI.
    """

    class Meta:
        model = Publisher
        fields = ["name", "description"]

class RegistrationForm(UserCreationForm):
    """
    Registration form for creating a new user account.

    Allows the user to choose a role at signup. To avoid privilege escalation,
    we only allow Reader and Journalist to be selected at registration time.
    Editors should be created/assigned by an admin.
    """

    role = forms.ChoiceField(
        choices=(
            (User.Role.READER, "Reader"),
            (User.Role.JOURNALIST, "Journalist"),
        ),
        initial=User.Role.READER,
        help_text="Choose Reader (subscribe + API feed) or Journalist (submit articles for review).",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "role")

    def save(self, commit: bool = True):
        """
        Create the user and apply the selected role.

        Args:
            commit (bool): Whether to save the user to the database.

        Returns:
            User: The created user instance.
        """
        user = super().save(commit=False)
        user.role = self.cleaned_data["role"]
        if commit:
            user.save()
        return user