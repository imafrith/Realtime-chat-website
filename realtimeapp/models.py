from django.db import models
from django.contrib.auth.models import User
import shortuuid
# Create your models here.
class Profile(models.Model):
    Gender_choices=(

        (1,'male'),
        (2,'female'),
        (3,'others')
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(default = 'This is the default, title change it in profile',max_length=500, blank=True)
    phone_number = models.CharField(max_length=12, blank=True)
    birth_date = models.DateField(default="2000-05-20",null=True, blank=True)
    address=models.TextField(max_length=250,blank=True,null=True,default="Add Address")
    city=models.CharField(max_length=250,blank=True,null=True ,default="Add Address")
    Landmark=models.CharField(max_length=250,blank=True,null=True,default="Add Address")
    pincode=models.IntegerField(null=True,blank=True)
    profile_image = models.ImageField(default='static/assets/images/pro.png', upload_to='users/', null=True, blank=True)
    Gender=models.PositiveSmallIntegerField(choices=Gender_choices,null=True,blank=True)

    def __str__(self):
        return '%s %s' % (self.user.first_name, self.user.last_name)
    


class Chatgroup(models.Model):
    group_name=models.CharField(max_length=500, unique=True,default=shortuuid.uuid)
    users_online=models.ManyToManyField(User,related_name='online_in_group',blank=True)
    member=models.ManyToManyField(User,related_name='chat_groups',blank=True)
    is_private=models.BooleanField(default=False)
  

    def __str__(self):
        return self.group_name
    
class GroupMessage(models.Model):
    group=models.ForeignKey(Chatgroup,related_name='chat_messages',on_delete=models.CASCADE)
    author=models.ForeignKey(User,on_delete=models.CASCADE)
    body=models.CharField(max_length=500)
    created=models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False) 
   

    def __str__(self):
        return f"{self.author}: {self.body}"
    class Meta:
        ordering=['-created']



