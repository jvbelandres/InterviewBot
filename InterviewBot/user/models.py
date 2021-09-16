from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here. 
#def image_upload_path(instance, filename):
#	return "{}/{}".format(instance.applicant.lastname, filename)

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
		user.is_active = True
		user.save(using=self._db)
		return user

class Account(AbstractBaseUser):
	email = models.EmailField(verbose_name="email", max_length=60, unique="True")
	is_active = models.BooleanField(default=False)
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
    is_deleted = models.BooleanField(default=False)
    is_default = models.BooleanField(default=True)

    # questions from https://bit.ly/3vGcAav
    question_1 = models.CharField(max_length = 250, null=True, blank=True, default='Please tell me about yourself.', editable=False)
    question_2 = models.CharField(max_length = 250, null=True, blank=True, default='What does team spirit mean to you and how would you go about building it?', editable=False)
    question_3 = models.CharField(max_length = 250, null=True, blank=True, default='Your project fails miserably. How do you deal with it?', editable=False)
    question_4 = models.CharField(max_length = 250, null=True, blank=True, default='How do you go about rearranging your schedule if something unplanned occurs?', editable=False)
    question_5 = models.CharField(max_length = 250, null=True, blank=True, default='What can you do for us that other candidates cannot?', editable=False)
    question_6 = models.CharField(max_length = 250, null=True, blank=True, default='Describe a situation where results went against expectations. How did you adapt to this change?', editable=False)
    question_7 = models.CharField(max_length = 250, null=True, blank=True, default='What are the key ingredients to building good relationships with others?', editable=False)
    question_8 = models.CharField(max_length = 250, null=True, blank=True, default='Tell me about a time when you’ve struggled to meet deadlines. What did you do?', editable=False)
    question_9 = models.CharField(max_length = 250, null=True, blank=True, default='What would you do if you discovered a manager was breaking company rules?', editable=False)
    question_10 = models.CharField(max_length = 250, null=True, blank=True, default=' What steps do you take to gain a customer’s trust?', editable=False)
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
    weight11 = models.IntegerField(null=True, blank=True)
    weight12 = models.IntegerField(null=True, blank=True)
    weight13 = models.IntegerField(null=True, blank=True)
    weight14 = models.IntegerField(null=True, blank=True)
    weight15 = models.IntegerField(null=True, blank=True)
    weight16 = models.IntegerField(null=True, blank=True)
    weight17 = models.IntegerField(null=True, blank=True)
    weight18 = models.IntegerField(null=True, blank=True)
    weight19 = models.IntegerField(null=True, blank=True)
    weight20 = models.IntegerField(null=True, blank=True)
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
    timer11 = models.IntegerField(null=True, blank=True)
    timer12 = models.IntegerField(null=True, blank=True)
    timer13 = models.IntegerField(null=True, blank=True)
    timer14 = models.IntegerField(null=True, blank=True)
    timer15 = models.IntegerField(null=True, blank=True)
    timer16 = models.IntegerField(null=True, blank=True)
    timer17 = models.IntegerField(null=True, blank=True)
    timer18 = models.IntegerField(null=True, blank=True)
    timer19 = models.IntegerField(null=True, blank=True)
    timer20 = models.IntegerField(null=True, blank=True)

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
	# positive1 = models.FloatField(null=True, blank=True)
	# positive2 = models.FloatField(null=True, blank=True)
	# positive3 = models.FloatField(null=True, blank=True)
	# positive4 = models.FloatField(null=True, blank=True)
	# positive5 = models.FloatField(null=True, blank=True)
	# positive6 = models.FloatField(null=True, blank=True)
	# positive7 = models.FloatField(null=True, blank=True)
	# positive8 = models.FloatField(null=True, blank=True)
	# positive9 = models.FloatField(null=True, blank=True)
	# positive10 = models.FloatField(null=True, blank=True)
	# positive11 = models.FloatField(null=True, blank=True)
	# positive12 = models.FloatField(null=True, blank=True)
	# positive13 = models.FloatField(null=True, blank=True)
	# positive14 = models.FloatField(null=True, blank=True)
	# positive15 = models.FloatField(null=True, blank=True)
	# positive16 = models.FloatField(null=True, blank=True)
	# positive17 = models.FloatField(null=True, blank=True)
	# positive18 = models.FloatField(null=True, blank=True)
	# positive19 = models.FloatField(null=True, blank=True)
	# positive20 = models.FloatField(null=True, blank=True)
	score1 = models.FloatField(null=True, blank=True)
	score2 = models.FloatField(null=True, blank=True)
	score3 = models.FloatField(null=True, blank=True)
	score4 = models.FloatField(null=True, blank=True)
	score5 = models.FloatField(null=True, blank=True)
	score6 = models.FloatField(null=True, blank=True)
	score7 = models.FloatField(null=True, blank=True)
	score8 = models.FloatField(null=True, blank=True)
	score9 = models.FloatField(null=True, blank=True)
	score10 = models.FloatField(null=True, blank=True)
	score11 = models.FloatField(null=True, blank=True)
	score12 = models.FloatField(null=True, blank=True)
	score13 = models.FloatField(null=True, blank=True)
	score14 = models.FloatField(null=True, blank=True)
	score15 = models.FloatField(null=True, blank=True)
	score16 = models.FloatField(null=True, blank=True)
	score17 = models.FloatField(null=True, blank=True)
	score18 = models.FloatField(null=True, blank=True)
	score19 = models.FloatField(null=True, blank=True)
	score20 = models.FloatField(null=True, blank=True)
	final_score = models.FloatField(null=True, blank=True)

	class Meta:
		db_table = "AppliedJob"