from django.db import models

# Create your models here.


class User(models.Model):
    """
    Model for storing users of the game
    """
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255, null=True)
    email = models.EmailField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username


class Picture(models.Model):
    """
    The picture model saves  Picture details and also work as a votes ledger
    """
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=20, null=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    up_votes_account = models.IntegerField(default=0)
    down_votes_account = models.IntegerField(default=0)


class Images(models.Model):
    """
    Each Image belongs to a picture Detail using ImageId as the picture pk
    """
    base64Image = models.TextField()
    picture_details = models.ForeignKey(Picture, on_delete=models.CASCADE, blank=True)


class VotingHistory(models.Model):
    """
    A user should only have one vote per picture
    This stores all votes per user<->picture relationship and it should add up to the ledge figures
    """
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    picture_id = models.ForeignKey(Picture, on_delete=models.CASCADE)
    vote_type = models.NullBooleanField()
    up_votes_balance_before = models.IntegerField()
    up_votes_balance_after = models.IntegerField()
    down_votes_balance_before = models.IntegerField()
    down_votes_balance_after = models.IntegerField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('user_id', 'picture_id'),)
