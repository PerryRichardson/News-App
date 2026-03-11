from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm

from .models import Article, Publisher, User


class ArticleForm(forms.ModelForm):
    """Form for journalists to create a new article."""

    class Meta:
        model = Article
        fields = ["title", "body", "publisher"]


class PublisherForm(forms.ModelForm):
    """Form for editors to create a Publisher through the web UI."""

    class Meta:
        model = Publisher
        fields = ["name", "description"]


class RegistrationForm(UserCreationForm):
    """
    Registration form for creating a new user account.

    Users can register as Reader or Journalist freely.
    Editor registration requires a valid invite code.
    """

    email = forms.EmailField(
        required=True,
        help_text="Required. Used for notifications and account communication.",
    )

    role = forms.ChoiceField(
        choices=(
            (User.Role.READER, "Reader"),
            (User.Role.JOURNALIST, "Journalist"),
            (User.Role.EDITOR, "Editor (invite code required)"),
        ),
        initial=User.Role.READER,
        help_text="Choose a role. Editor requires an invite code.",
    )

    editor_invite_code = forms.CharField(
        required=False,
        strip=True,
        help_text="Only required if you are registering as an Editor.",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "role", "editor_invite_code")

    def clean(self):
        """
        Validate Editor signups require a correct invite code.
        """
        cleaned = super().clean()
        role = cleaned.get("role")
        code = (cleaned.get("editor_invite_code") or "").strip()

        if role == User.Role.EDITOR:
            expected = getattr(settings, "EDITOR_INVITE_CODE", "")
            if not expected or code != expected:
                raise forms.ValidationError(
                    "Invalid editor invite code. Please choose a different role."
                )

        return cleaned

    def save(self, commit: bool = True):
        """
        Create the user and assign the selected role.

        Args:
            commit: Whether to save the user to the database.

        Returns:
            The created user instance.
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.role = self.cleaned_data["role"]

        if commit:
            user.save()

        return user