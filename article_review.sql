-- Adminer 5.4.0 PostgreSQL 17.6 dump

CREATE SEQUENCE articles_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1;

CREATE TABLE "public"."articles" (
    "id" integer DEFAULT nextval('articles_id_seq') NOT NULL,
    "author_id" integer NOT NULL,
    "category" character varying(100) NOT NULL,
    "title" character varying(200) NOT NULL,
    "content" text NOT NULL,
    "status" character varying(20) DEFAULT 'draft' NOT NULL,
    "created_at" timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updated_at" timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT "articles_pkey" PRIMARY KEY ("id")
)
WITH (oids = false);


CREATE SEQUENCE users_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1;

CREATE TABLE "public"."users" (
    "id" integer DEFAULT nextval('users_id_seq') NOT NULL,
    "username" character varying(50) NOT NULL,
    "role" character varying(10) NOT NULL,
    CONSTRAINT "users_pkey" PRIMARY KEY ("id")
)
WITH (oids = false);

CREATE UNIQUE INDEX users_username_key ON public.users USING btree (username);


ALTER TABLE ONLY "public"."articles" ADD CONSTRAINT "articles_author_id_fkey" FOREIGN KEY (author_id) REFERENCES users(id) NOT DEFERRABLE;

-- 2026-11-14 08:48:47 UTC
 -- 限制使用者只能是作者或編輯
ALTER TABLE public.users
ADD CONSTRAINT users_role_check
CHECK (role IN ('author', 'editor'));

-- 限制稿件只能有三種審查狀態
ALTER TABLE public.articles
ADD CONSTRAINT articles_status_check
CHECK (status IN ('draft', 'reviewing', 'approved'));