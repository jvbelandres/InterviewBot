from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

User = settings.AUTH_USER_MODEL

# Create your models here. 
def image_upload_path(instance, filename):
	return "{}/{}".format(instance.applicant.lastname, filename)

class AccountManager(BaseUserManager):
	def create_user(self, email, firstname, lastname, gender, phone, password, active=True,
		staff=False, admin=False):
		if not email:
			raise ValueError("Users must have an email address")
		if not password:
			raise ValueError("Users must have a password")

		user = self.model(
				email=self.normalize_email(email),
				firstname = firstname,
				lastname = lastname,
				gender = gender,
				phone = phone,
		)

		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_staffuser(self, email, firstname, lastname, gender, password, phone):
		user = self.create_user(
			email,
			firstname=firstname,
			lastname=lastname,
			gender=gender,
			phone=phone,
			password=password,
		)
		user.staff = True
		user.save(using=self._db)
		return user

	def create_superuser(self, email, firstname, lastname, gender, phone, password):
		user = self.create_user(
			email=self.normalize_email(email),
			firstname = firstname,
			password = password,
			lastname = lastname,
			gender = gender,
			phone = phone,
		)
		user.staff = True
		user.admin = True
		user.save(using=self._db)
		return user

class Account(AbstractBaseUser):
	email = models.EmailField(verbose_name="email", max_length=60, unique="True")
	is_active = models.BooleanField(default=True)
	staff = models.BooleanField(default=False)
	admin = models.BooleanField(default=False)

	firstname = models.CharField(max_length=70, null=True,blank=True)
	lastname = models.CharField(max_length=70, null=True,blank=True)
	phone = models.CharField(max_length=11)
	password = models.CharField(max_length=250, null=True, blank=True)
	gender = models.CharField(max_length=10, null=True, blank=True)

	USERNAME_FIELD = 'email' #use email to login
	REQUIRED_FIELDS = ['firstname', 'lastname', 'password', 'gender', 'phone']

	objects = AccountManager()

	def __str__(self):
		return self.email

	def has_perm(self, perm, obj=None):
		return True

	def has_module_perms(self, app_label):
		return True

	@property
	def is_staff(self):
		return self.staff
	
	@property
	def is_admin(self):
		return self.admin
	
	class Meta:
		db_table = "Account"

class Contact(models.Model):
	email = models.EmailField(max_length=50)
	subject = models.CharField(max_length = 50)
	message = models.CharField(max_length = 500)

	class Meta:
		db_table = "Contact"

class CreateJob(models.Model):
    admin = models.ForeignKey('user.Account', null = False, blank = False, on_delete = models.CASCADE)
    title = models.CharField(max_length = 50, null=True, blank=True)
    description = models.CharField(max_length = 500, null=True, blank=True)

    question_1 = models.CharField(max_length = 250, null=True, blank=True, default='Please tell me about yourself.', editable=False)
    question_2 = models.CharField(max_length = 250, null=True, blank=True, default='What do you consider as your weakness?', editable=False)
    question_3 = models.CharField(max_length = 250, null=True, blank=True, default='What are your goals?', editable=False)
    question_4 = models.CharField(max_length = 250, null=True, blank=True, default='What are your actions if employees disagreed with your decision?', editable=False)
    question_5 = models.CharField(max_length = 250, null=True, blank=True, default='What can you do for us that other candidates cannot?', editable=False)
    question_6 = models.CharField(max_length = 250, null=True, blank=True, default='Describe a situation where results went against expectations. How did you adapt to this change?', editable=False)
    question_7 = models.CharField(max_length = 250, null=True, blank=True, default='Can you discuss a time where you had to manage your team through a difficult situation?', editable=False)
    question_8 = models.CharField(max_length = 250, null=True, blank=True, default='How do you prioritize your tasks when you have multiple deadlines to meet?', editable=False)
    question_9 = models.CharField(max_length = 250, null=True, blank=True, default='What is the most significant problem you solved in the workplace?', editable=False)
    question_10 = models.CharField(max_length = 250, null=True, blank=True, default='How do you explain new topics to coworkers unfamiliar with them?', editable=False)
    question_11 = models.CharField(max_length = 250, null=True, blank=True)
    question_12 = models.CharField(max_length = 250, null=True, blank=True)
    question_13 = models.CharField(max_length = 250, null=True, blank=True)
    question_14 = models.CharField(max_length = 250, null=True, blank=True)
    question_15 = models.CharField(max_length = 250, null=True, blank=True)
    question_16 = models.CharField(max_length = 250, null=True, blank=True)
    question_17 = models.CharField(max_length = 250, null=True, blank=True)
    question_18 = models.CharField(max_length = 250, null=True, blank=True)
    question_19 = models.CharField(max_length = 250, null=True, blank=True)
    question_20 = models.CharField(max_length = 250, null=True, blank=True)
    weight1 = models.IntegerField(null=True, blank=True)
    weight2 = models.IntegerField(null=True, blank=True)
    weight3 = models.IntegerField(null=True, blank=True)
    weight4 = models.IntegerField(null=True, blank=True)
    weight5 = models.IntegerField(null=True, blank=True)
    weight6 = models.IntegerField(null=True, blank=True)
    weight7 = models.IntegerField(null=True, blank=True)
    weight8 = models.IntegerField(null=True, blank=True)
    weight9 = models.IntegerField(null=True, blank=True)
    weight10 = models.IntegerField(null=True, blank=True)
    timer1 = models.IntegerField(null=True, blank=True)
    timer2 = models.IntegerField(null=True, blank=True)
    timer3 = models.IntegerField(null=True, blank=True)
    timer4 = models.IntegerField(null=True, blank=True)
    timer5 = models.IntegerField(null=True, blank=True)
    timer6 = models.IntegerField(null=True, blank=True)
    timer7 = models.IntegerField(null=True, blank=True)
    timer8 = models.IntegerField(null=True, blank=True)
    timer9 = models.IntegerField(null=True, blank=True)
    timer10 = models.IntegerField(null=True, blank=True)

    class Meta: 
        db_table = "JobOfferings"
		
class SavedJob(models.Model):
	user = models.ForeignKey(Account, null=False, blank=False, on_delete=models.CASCADE)
	job = models.ForeignKey(CreateJob, null=False, blank=False, on_delete=models.CASCADE)

	class Meta:
		db_table ="SavedJob"

class AppliedJob(models.Model):
	user = models.ForeignKey(Account, null = False, blank = False, on_delete = models.CASCADE, related_name = "Applicant")
	job = models.ForeignKey(CreateJob, null = False, blank = False, on_delete = models.CASCADE, related_name = "CreateJob")
	response_1 = models.TextField(null = True)
	response_2 = models.TextField(null = True)
	response_3 = models.TextField(null = True)
	response_4 = models.TextField(null = True)
	response_5 = models.TextField(null = True)
	response_6 = models.TextField(null = True)
	response_7 = models.TextField(null = True)
	response_8 = models.TextField(null = True)
	response_9 = models.TextField(null = True)
	response_10 = models.TextField(null = True)
	response_11 = models.TextField(null = True)
	response_12 = models.TextField(null = True)
	response_13 = models.TextField(null = True)
	response_14 = models.TextField(null = True)
	response_15 = models.TextField(null = True)
	response_16 = models.TextField(null = True)
	response_17 = models.TextField(null = True)
	response_18 = models.TextField(null = True)
	response_19 = models.TextField(null = True)
	response_20 = models.TextField(null = True)
	requirement_1 = models.CharField(max_length = 250, null=True, blank=True)
	label1 = models.CharField(max_length=10, null=True, blank=True)
	label2 = models.CharField(max_length=10, null=True, blank=True)
	label3 = models.CharField(max_length=10, null=True, blank=True)
	label4 = models.CharField(max_length=10, null=True, blank=True)
	label5 = models.CharField(max_length=10, null=True, blank=True)
	label6 = models.CharField(max_length=10, null=True, blank=True)
	label7 = models.CharField(max_length=10, null=True, blank=True)
	label8 = models.CharField(max_length=10, null=True, blank=True)
	label9 = models.CharField(max_length=10, null=True, blank=True)
	label10 = models.CharField(max_length=10, null=True, blank=True)
	label11 = models.CharField(max_length=10, null=True, blank=True)
	label12 = models.CharField(max_length=10, null=True, blank=True)
	label13 = models.CharField(max_length=10, null=True, blank=True)
	label14 = models.CharField(max_length=10, null=True, blank=True)
	label15 = models.CharField(max_length=10, null=True, blank=True)
	label16 = models.CharField(max_length=10, null=True, blank=True)
	label17 = models.CharField(max_length=10, null=True, blank=True)
	label18 = models.CharField(max_length=10, null=True, blank=True)
	label19 = models.CharField(max_length=10, null=True, blank=True)
	label20 = models.CharField(max_length=10, null=True, blank=True)
	positive1 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	positive2 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	positive3 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	positive4 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	positive5 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	positive6 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	positive7 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	positive8 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	positive9 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	positive10 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	positive11 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	positive12 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	positive13 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	positive14 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	positive15 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	positive16 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	positive17 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	positive18 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	positive19 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	positive20 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	negative1 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	negative2 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	negative3 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	negative4 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	negative5 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	negative6 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	negative7 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	negative8 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	negative9 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	negative10 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	negative11 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	negative12 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	negative13 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	negative14 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	negative15 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	negative16 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	negative17 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	negative18 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	negative19 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	negative20 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	neutral1 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	neutral2 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	neutral3 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	neutral4 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	neutral5 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	neutral6 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	neutral7 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	neutral8 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	neutral9 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	neutral10 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	neutral11 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	neutral12 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	neutral13 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	neutral14 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	neutral15 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	neutral16 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	neutral17 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	neutral18 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	neutral19 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	neutral20 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	score1 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	score2 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	score3 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	score4 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	score5 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	score6 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	score7 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	score8 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	score9 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	score10 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	score11 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	score12 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	score13 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	score14 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	score15 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	score16 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	score17 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	score18 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	score19 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
	score20 = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)

	class Meta:
		db_table = "AppliedJob"