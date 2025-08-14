--
-- PostgreSQL database dump
--

-- Dumped from database version 17.2 (Debian 17.2-1.pgdg110+1)
-- Dumped by pg_dump version 17.2 (Debian 17.2-1.pgdg110+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: ansibleconfig; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ansibleconfig (
    hash text,
    contents bytea
);


ALTER TABLE public.ansibleconfig OWNER TO postgres;

--
-- Name: ansibleplaybook; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ansibleplaybook (
    hash text,
    contents bytea
);


ALTER TABLE public.ansibleplaybook OWNER TO postgres;

--
-- Name: jupyternotebook; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.jupyternotebook (
    hash text NOT NULL,
    contents bytea
);


ALTER TABLE public.jupyternotebook OWNER TO postgres;

--
-- Name: logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.logs (
    hash text,
    contents bytea
);


ALTER TABLE public.logs OWNER TO postgres;

--
-- Data for Name: ansibleconfig; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ansibleconfig (hash, contents) FROM stdin;
\.


--
-- Data for Name: ansibleplaybook; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ansibleplaybook (hash, contents) FROM stdin;
\.


--
-- Data for Name: jupyternotebook; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.jupyternotebook (hash, contents) FROM stdin;
\.


--
-- Data for Name: logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.logs (hash, contents) FROM stdin;
\.


--
-- Name: ansibleconfig ansibleconfig_hash_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ansibleconfig
    ADD CONSTRAINT ansibleconfig_hash_key UNIQUE (hash);


--
-- Name: ansibleplaybook ansibleplaybook_hash_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ansibleplaybook
    ADD CONSTRAINT ansibleplaybook_hash_key UNIQUE (hash);


--
-- Name: jupyternotebook jupyternotebook_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jupyternotebook
    ADD CONSTRAINT jupyternotebook_pkey PRIMARY KEY (hash);


--
-- Name: logs logs_hash_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.logs
    ADD CONSTRAINT logs_hash_key UNIQUE (hash);


--
-- PostgreSQL database dump complete
--

