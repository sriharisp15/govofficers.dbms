alter table officers add column officers_id int;
SELECT officer_id, department, dept_id FROM officers;
SELECT officers_id, department, dept_id FROM officers;
ALTER TABLE officers
ADD CONSTRAINT fk_dept
FOREIGN KEY (dept_id) REFERENCES departments(dept_id);