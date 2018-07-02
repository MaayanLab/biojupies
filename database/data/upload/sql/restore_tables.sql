RENAME TABLE `platform` TO `platform_{version}`;
RENAME TABLE `dataset` TO `dataset_{version}`;
RENAME TABLE `sample` TO `sample_{version}`;
RENAME TABLE `sample_metadata` TO `sample_metadata_{version}`;

RENAME TABLE `platform_old` TO `platform`;
RENAME TABLE `dataset_old` TO `dataset`;
RENAME TABLE `sample_old` TO `sample`;
RENAME TABLE `sample_metadata_old` TO `sample_metadata`;
