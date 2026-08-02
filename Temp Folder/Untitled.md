select p1.email ,(select count(*) from person p2

    where p1.email = p2.email) as cnt from  person p1


| id  | email                     |
| --- | ------------------------- |
| 1   | [a@b.com](mailto:a@b.com) |
| 2   | [c@d.com](mailto:c@d.com) |
| 3   | [a@b.com](mailto:a@b.com) |





