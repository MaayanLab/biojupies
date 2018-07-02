RENAME TABLE `platform` TO `platform_old`;
RENAME TABLE `dataset` TO `dataset_old`;
RENAME TABLE `sample` TO `sample_old`;
RENAME TABLE `sample_metadata` TO `sample_metadata_old`;

RENAME TABLE `platform_{version}` TO `platform`;
RENAME TABLE `dataset_{version}` TO `dataset`;
RENAME TABLE `sample_{version}` TO `sample`;
RENAME TABLE `sample_metadata_{version}` TO `sample_metadata`;