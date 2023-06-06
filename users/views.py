# 导入响应
from django.shortcuts import render, HttpResponse, reverse, redirect
# 导入常量
from constants import INVALID_KIND
# 导入格式
from users.forms import UserLoginForm, AdminLoginForm, UserRegisterForm, UserUpdateForm
# 导入模型
from users.models import Admin, User
# 导入视图函数
from django.views.generic import CreateView, UpdateView


# Create your views here.

def all_users():
    return User.objects.all().values()


def display_all_users():
    print("正在输出所有用户")
    user = all_users()
    for i in range(user.count()):
        print(user[i])


def back(request):
    return render(request, "background.html")


def home(request):
    return render(request, "login_home.html")


def login(request, *args, **kwargs):
    if not kwargs or "kind" not in kwargs or kwargs["kind"] not in ["Admin", "User"]:
        return HttpResponse(INVALID_KIND)

    kind = kwargs["kind"]

    if request.method == 'POST':
        if kind == "Admin":
            form = AdminLoginForm(data=request.POST)
        else:
            form = UserLoginForm(data=request.POST)

        if form.is_valid():
            uid = form.cleaned_data["uid"]
            if len(uid) != 10:
                form.add_error("uid", "账号长度必须为10")
            else:
                if kind == "Admin":
                    number = uid
                    object_set = Admin.objects.filter(admin_number=number)
                else:
                    number = uid
                    object_set = User.objects.filter(client_number=number)
                if object_set.count() == 0:
                    form.add_error("uid", "该账号未注册.")
                else:
                    user = object_set[0]
                    if form.cleaned_data["password"] != user.password:
                        form.add_error("password", "密码不正确.")
                    else:
                        request.session['kind'] = kind
                        request.session['user'] = uid
                        request.session['id'] = user.id
                        # successful login
                        to_url = reverse("vocabulary", kwargs={'kind': kind})
                        return redirect(to_url)

            return render(request, 'login_detail.html', {'form': form, 'kind': kind})
    else:
        context = {'kind': kind}
        if request.GET.get('uid'):
            uid = request.GET.get('uid')
            context['uid'] = uid
            if kind == "Admin":
                form = AdminLoginForm({"uid": uid, 'password': '12345678'})
            else:
                form = UserLoginForm({"uid": uid, 'password': '12345678'})
        else:
            if kind == "Admin":
                form = AdminLoginForm()
            else:
                form = UserLoginForm()
        context['form'] = form
        if request.GET.get('from_url'):
            context['from_url'] = request.GET.get('from_url')

        return render(request, 'login_detail.html', context)


class CreateUserView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = "register.html"
    success_url = "login"

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        if form.is_valid():
            return self.form_valid(form)
        else:
            self.object = None
            return self.form_invalid(form)

    def form_valid(self, form):
        # order_by默认升序排列，number前的负号表示降序排列
        user_set = User.objects.filter().order_by("-client_number")
        if user_set.count() > 0:
            last_user = user_set[0]
            new_client_number = str(int(last_user.client_number) + 1)
            for i in range(10 - len(new_client_number)):
                new_client_number = "0" + new_client_number
        else:
            new_client_number = "0000000001"

        # Create, but don't save the new user instance.
        new_user = form.save(commit=False)
        # Modify the student
        new_user.client_number = new_client_number
        # Save the new instance.
        new_user.save()
        # Now, save the many-to-many data for the form.
        form.save_m2m()

        self.object = new_user

        from_url = "register"
        base_url = reverse(self.get_success_url(), kwargs={'kind': 'User'})
        return redirect(base_url + '?uid=%s&from_url=%s' % (new_client_number, from_url))


def register(request, kind):
    func = None
    if kind == "User":
        func = CreateUserView.as_view()

    if func:
        return func(request)
    else:
        return HttpResponse(INVALID_KIND)


def logout(request):
    for sv in {"kind", "user", "id"}:
        if request.session.get(sv):
            del request.session[sv]

    return redirect("login")


class UpdateUserView(UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "update.html"

    def get_context_data(self, **kwargs):
        context = super(UpdateUserView, self).get_context_data()
        context.update(kwargs)
        context["kind"] = "User"

        return context

    def get_success_url(self):
        return reverse("vocabulary", kwargs={"kind": "User"})


def update(request, kind):
    func = None
    if kind == "User":
        func = UpdateUserView.as_view()
    else:
        return HttpResponse(INVALID_KIND)

    pk = request.session.get("id")
    if pk:
        context = {
            "name": request.session.get("name", ""),
            "kind": request.session.get("kind", "")
        }
        return func(request, pk=pk, context=context)

    return redirect("login")
