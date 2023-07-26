OBS_PROJECT := EA4-experimental
OBS_PACKAGE := ea-nginx-passenger
DISABLE_BUILD := arch=i586 repository=CentOS_6.5_standard
include $(EATOOLS_BUILD_DIR)obs.mk
