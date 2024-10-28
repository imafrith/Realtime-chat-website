from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from .form import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.http import Http404



from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Chatgroup, GroupMessage
from django.core.exceptions import ObjectDoesNotExist


# Create your views here.


@login_required
def index(request):
    
    return render(request,'page/index.html')

def group(request):
    chatgroup=Chatgroup.objects.filter(is_private=False)
    return render(request,'page/group.html',{'chatgroup':chatgroup})



def profile(request): 
    
    return render(request,'profile/profile.html')


class ProfileUpdateView(LoginRequiredMixin, TemplateView):
   
    profile_form = ProfileForm
    template_name = 'profile/profileupdate.html'

    def post(self, request):

        post_data = request.POST or None
        file_data = request.FILES or None
      

        user_form = UserForm(post_data, instance=request.user)
       
        profile_form = ProfileForm(post_data, file_data,instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.error(request, 'Your profile is updated successfully!')
            return HttpResponseRedirect('/profile')
     

        context = self.get_context_data(
             
                                        user_form=user_form,
                                        profile_form=profile_form
                                    )

        return self.render_to_response(context)     

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
def signin(request):
        if request.method=='POST':
            username=request.POST.get('username')
            password=request.POST.get('password')
            myuser =authenticate(username =username, password = password)
            if myuser is not None:
                login(request,myuser)
                return redirect('/')
            else:
                messages.info(request, 'Username or password is incorrect')
                return redirect('/login')
        return render(request,'page/signin.html')

def register(request):


    if request.method=='POST':
        firstname=request.POST.get('firstname')
        lastname=request.POST.get('lastname')
        username=request.POST.get('username')
        email=request.POST.get('email')
        password=request.POST.get('password')
        confirmpassword=request.POST.get('confirmpassword')
           
        if password != confirmpassword:
           messages.success(request,"Password Doesnot Match")
           return redirect('/register')
        if User.objects.filter(username = username).first():
            messages.error(request, "This username is already taken")
            return redirect('/register')
        elif User.objects.filter(email = email).first():
            messages.error(request, "This email is already register Go to login page")
            return redirect('/register')
        else:
            user=User.objects.create_user(username=username,email=email,password=password)
            User.first_name=firstname
            User.last_name=lastname
            user.save()
            messages.error(request, "Account Registered SucessFully")  
            return redirect('/login') 
    return render(request,'page/auth-register.html')




@login_required
def chat_view(request,name):
    chat_group=get_object_or_404(Chatgroup,group_name=name)
    GroupMessage.objects.filter(group=name, is_read=False).exclude(author=request.user).update(is_read=True)
    chat_messages=chat_group.chat_messages.all()[:30]
    if request.htmx:
        author = request.user
        body = request.POST.get('body')
        # Create and save the new chat message
        new_message = GroupMessage(group=chat_group, author=author, body=body)
        new_message.save()
        context={
            'message':new_message,
            'user':request.user
        }
        return render(request,'partials/chat_message_p.html',context)

      
    
    return render(request,'page/chatsgroup.html',{'chat_messages':chat_messages,'chat_group':chat_group})

def contact(request):
    profile = Profile.objects.exclude(user=request.user)
    return render(request,'page/contact.html',{'profile':profile})


@login_required
def get_or_create_chatroom(request, username):
    if request.user.username == username:
        return redirect('home')
    
    other_user = User.objects.get(username = username)
    my_chatrooms = request.user.chat_groups.filter(is_private=True)
    
    
    if my_chatrooms.exists():
        for chatroom in my_chatrooms:
            if other_user in chatroom.member.all():
                chatroom = chatroom
                break
            else:
                chatroom = Chatgroup.objects.create(is_private = True)
                chatroom.member.add(other_user, request.user)
    else:
        chatroom = Chatgroup.objects.create(is_private = True)
        chatroom.member.add(other_user, request.user)
        
    return redirect('chatroom', chatroom.group_name)


def chat_view_private(request,chatroom_name='public-chat'):
    chat_group=get_object_or_404(Chatgroup,group_name=chatroom_name)
  
    chat_messages=chat_group.chat_messages.all()[:30]

 
    other_user=None
    if chat_group.is_private:
        if request.user not in chat_group.member.all():
            raise Http404()
        for member in chat_group.member.all():
            if member != request.user:
                other_user=member
                break
   
    if request.htmx:
        author = request.user
        body = request.POST.get('body')
        # Create and save the new chat message
        new_message = GroupMessage(group=chat_group, author=author, body=body)
        new_message.save()
        context={
            'message':new_message,
            'user':request.user
        }
        return render(request,'partials/chat_message_p.html',context)
    context={
        'chat_messages':chat_messages,
        'other_user':other_user,
        'chatroom_name':chatroom_name,
    }
    return render(request,'page/chatprivate.html',context)

def contact(request):
    profile = Profile.objects.exclude(user=request.user)
    return render(request,'page/contact.html',{'profile':profile})





def logoutuser(request):

    logout(request)
    messages.info(request, 'Logout Sucessfully')
    return redirect('/login')





def chatsdisplay(request):
    # Get all private chat groups the user is a member of
    chatsroom = Chatgroup.objects.filter(member=request.user, is_private=True)
    
    # Dictionary to hold the latest chat for each user and new message count
    latest_chats = {}

    for chat in chatsroom:
        # Fetching all unique members of this chat group except the current user
        members = chat.member.exclude(pk=request.user.pk)
        
        for member in members:
            try:
                # Try to get the latest message from this member
                latest_message = GroupMessage.objects.filter(group=chat, author=member).latest('created')
                # Count unread messages for this member in the chat group
                unread_count = GroupMessage.objects.filter(group=chat, author=member, is_read=False).count()
            except ObjectDoesNotExist:
                # Handle the case where no messages exist (unlikely if chat exists)
                latest_message = None
                unread_count = 0

            # Store in dictionary if it's the latest message
            if latest_message:
                if member not in latest_chats or latest_message.created > latest_chats[member]['message'].created:
                    latest_chats[member] = {'message': latest_message, 'count': unread_count}

    # Convert the dictionary to a list of messages for the template
    latest_chats_list = []
    for member, data in latest_chats.items():
        latest_chats_list.append({
            'receiver': member,
            'message': data['message'],
            'new_message_count': data['count']
        })
    
    # Sort the list based on the most recent message
    latest_chats_list.sort(key=lambda x: x['message'].created, reverse=True)
    
    return render(request, 'page/chatsdisplay.html', {'latest_chat': latest_chats_list, 'chatsroom': chatsroom})


