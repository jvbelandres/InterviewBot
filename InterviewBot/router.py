from user.serializers import SavedJobSerializer
from user.viewsets import AccountViewset, AppliedJobViewset, ContactViewset, CreateJobViewset, SavedJobViewset
from rest_framework import routers

router = routers.DefaultRouter()
router.register('account', AccountViewset)
router.register('contact', ContactViewset)
router.register('job-offering', CreateJobViewset)
router.register('saved-job', SavedJobViewset)
router.register('applied-job', AppliedJobViewset)