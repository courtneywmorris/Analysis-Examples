## Context for Analytics Problems

You work at a social media site. You have to write a lot of queries to get the desired data and stats from the database.

You will be working with the following tables:

* `registrations`: One entry per user when the register
* `logins`: One entry every time a user logs in
* `optout`: A list of users which have opted out of receiving email
* `friends`: All friend connections. Note that while friend connections are mutual, sometimes this table has both directions and sometimes it doesn't. You should assume that if A is friends with B, B is friends with A even if both directions aren't in the table.
* `messages`: All messages users have sent
* `test_group`: A table for an A/B test


## Write Some SQL Queries
Each of these questions is a prompt for writing a SQL query. I answered the following questions with
a partner.


1. Get the number of users who have registered each day, ordered by date.

```sql
SELECT date_trunc('day', tmstmp) AS date, COUNT(userid)
FROM registrations
GROUP BY date
ORDER BY date DESC;
```

2. Which day of the week gets the most registrations?

```sql
SELECT week_day, MAX(A.c) m
FROM (SELECT date_part('dow', tmstmp) AS week_day, COUNT(userid) c
FROM registrations
GROUP BY week_day
ORDER BY week_day DESC) A
GROUP BY week_day
ORDER BY m
LIMIT 1;
```

3. You are sending an email to users who haven't logged in in the week before '2014-08-14' and have not opted out of receiving email. Write a query to select these users.

```sql
SELECT DISTINCT l.userid
FROM logins l
LEFT JOIN optout o
ON l.userid = o.userid
WHERE o.userid IS NULL AND l.tmstmp > '2014-08-7' AND l.tmstmp <= '2014-08-14'
ORDER BY l.userid;
```

4. For every user, get the number of users who registered on the same day as them. Hint: This is a self join (join the registrations table with itself).

```sql
SELECT r1.userid, date_trunc('day', tmstmp) AS date, r2.c
FROM registrations r1
JOIN
(SELECT date_trunc('day', tmstmp) AS date, COUNT(userid) c
FROM registrations
GROUP BY date
ORDER BY date) r2
ON date_trunc('day', r1.tmstmp)=r2.date;
```

5. You are running an A/B test and would like to target users who have logged in on mobile more times than web. You should only target users in test group A. Write a query to get all the targeted users.

```sql
SELECT userid, count(type) count, type
FROM logins
WHERE type='mobile'
GROUP BY userid, type
ORDER BY userid)
,

web AS (
SELECT userid, count(type) count, type
FROM logins
WHERE type='web'
GROUP BY userid, type
ORDER BY userid)


SELECT DISTINCT l.userid
FROM logins l
JOIN web ON l.userid=web.userid
JOIN mobile ON l.userid=mobile.userid AND mobile.count > web.count;
```

6. You would like to determine each user's most communicated with user. For each user, determine the user they exchange the most messages with (outgoing plus incoming).

```sql
CREATE TABLE msg_cnt AS

WITH senders as (
SELECT sender, COUNT(message) cnt, recipient
FROM messages
GROUP BY sender, recipient)
,

receivers as (
SELECT recipient, COUNT(message) cnt, sender
FROM messages
GROUP BY recipient, sender)
,

sums as (
SELECT senders.sender s, receivers.sender r, SUM(senders.cnt + receivers.cnt) total
FROM senders, receivers
WHERE senders.sender = receivers.recipient AND senders.recipient = receivers.sender
GROUP BY senders.sender, receivers.sender)
,

max as (
SELECT sums.s z, MAX(sums.total) mm
FROM sums
GROUP BY sums.s
)


SELECT sums.s, sums.r
FROM max, sums
WHERE max.mm = sums.total AND sums.s = max.z;
```

7. You could also consider the length of the messages when determining the user's most communicated with friend. Sum up the length of all the messages communicated between every pair of users and determine which one is the maximum. This should only be a minor change from the previous query.

```sql
CREATE TABLE msg_len AS

WITH senders as (
SELECT sender, char_length(message) len, recipient
FROM messages
GROUP BY sender, recipient, message)
,

receivers as (
SELECT recipient, char_length(message) len, sender
FROM messages
GROUP BY recipient, sender, message)
,

sums as (
SELECT senders.sender s, receivers.sender r, SUM(senders.len + receivers.len) total
FROM senders, receivers
WHERE senders.sender = receivers.recipient AND senders.recipient = receivers.sender
GROUP BY senders.sender, receivers.sender)
,

max as (
SELECT sums.s z, MAX(sums.total) mm
FROM sums
GROUP BY sums.s
)

SELECT sums.s, sums.r
FROM max, sums
WHERE max.mm = sums.total AND sums.s = max.z;
```

8. What percent of the time are the above two answers different?

```sql
SELECT SUM(A.ratio)/ CAST (COUNT(*) AS FLOAT)*100
FROM (SELECT c.s, c.r r1, l.r r2, CASE WHEN c.r = l.r THEN 1 ELSE 0 END ratio
FROM msg_cnt c
JOIN msg_len l
ON c.s=l.s) A;
```
