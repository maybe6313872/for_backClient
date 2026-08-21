-- 将 art 表的 thumbnail 字段从 BLOB 改为 LONGBLOB
-- 这样可以支持最大 4GB 的文件

ALTER TABLE `art` 
MODIFY COLUMN `thumbnail` LONGBLOB NOT NULL;
