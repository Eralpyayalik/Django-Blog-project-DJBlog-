from django.contrib.auth.tokens import PasswordResetTokenGenerator

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        # Kullanıcı ID, zaman ve aktiflik durumunu birleştirip şifreli bir kod yapar
        return (
            str(user.pk) + str(timestamp) + str(user.is_active)
        )

account_activation_token = AccountActivationTokenGenerator()