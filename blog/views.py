from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import CommentForm, EmailPostForm
from django.views.generic import ListView
from django.core.mail import send_mail


app_name = 'blog'

def index(request):
    return render(request, 'blog/index.html')


def post_list(request):
    object_list = Post.objects.all()
    paginator = Paginator(object_list, 3) # 3 posts per page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html', {'page':page, 'posts': posts})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, 
                             status='published', 
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    comments = post.comments.filter(active=True)
    new_comment = None
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False) # don't save to db immediately
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()
            
    return render(request, 'blog/post/detail.html', 
                  {'post': post,
                   'comments': comments,
                   'new_comment': new_comment,
                   'comment_form': comment_form})


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'
    
    
def post_share(request, post_id):
    # retrieve post by id
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    
    if request.method == 'POST':
        # form was submitted
        form = EmailPostForm(request.POST or None)
        if form.is_valid():
            # Form fields passed validation
            cd = form
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommend you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
                f"{cd['name']}\s comments: {cd['comments']}"
            send_mail(subject, message, 'admin@blog.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    
    return render(request, 'blog/post/share.html', 
                  {'post': post,
                    'form': form,
                    'sent': sent,})
            