--
-- PostgreSQL database dump
--

\restrict 2b40HfTyMnaefHUZJRS2Pv476xXqF6doZQBsTBfyY3VA6ViMQtNzEqd3GtYRIyE

-- Dumped from database version 15.15 (Debian 15.15-1.pgdg13+1)
-- Dumped by pg_dump version 15.15 (Debian 15.15-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE IF EXISTS ONLY public.tracks DROP CONSTRAINT IF EXISTS tracks_camera_id_fkey;
ALTER TABLE IF EXISTS ONLY public.detections DROP CONSTRAINT IF EXISTS detections_track_id_fkey;
ALTER TABLE IF EXISTS ONLY public.detections DROP CONSTRAINT IF EXISTS detections_camera_id_fkey;
ALTER TABLE IF EXISTS ONLY public.camera_streams DROP CONSTRAINT IF EXISTS camera_streams_camera_id_fkey;
DROP INDEX IF EXISTS public.ix_users_username;
DROP INDEX IF EXISTS public.ix_users_email;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_pkey;
ALTER TABLE IF EXISTS ONLY public.tracks DROP CONSTRAINT IF EXISTS tracks_pkey;
ALTER TABLE IF EXISTS ONLY public.detections DROP CONSTRAINT IF EXISTS detections_pkey;
ALTER TABLE IF EXISTS ONLY public.cameras DROP CONSTRAINT IF EXISTS cameras_pkey;
ALTER TABLE IF EXISTS ONLY public.camera_streams DROP CONSTRAINT IF EXISTS camera_streams_pkey;
ALTER TABLE IF EXISTS public.users ALTER COLUMN user_id DROP DEFAULT;
ALTER TABLE IF EXISTS public.tracks ALTER COLUMN track_id DROP DEFAULT;
ALTER TABLE IF EXISTS public.detections ALTER COLUMN detection_id DROP DEFAULT;
ALTER TABLE IF EXISTS public.cameras ALTER COLUMN camera_id DROP DEFAULT;
ALTER TABLE IF EXISTS public.camera_streams ALTER COLUMN stream_id DROP DEFAULT;
DROP SEQUENCE IF EXISTS public.users_user_id_seq;
DROP TABLE IF EXISTS public.users;
DROP SEQUENCE IF EXISTS public.tracks_track_id_seq;
DROP TABLE IF EXISTS public.tracks;
DROP SEQUENCE IF EXISTS public.detections_detection_id_seq;
DROP TABLE IF EXISTS public.detections;
DROP SEQUENCE IF EXISTS public.cameras_camera_id_seq;
DROP TABLE IF EXISTS public.cameras;
DROP SEQUENCE IF EXISTS public.camera_streams_stream_id_seq;
DROP TABLE IF EXISTS public.camera_streams;
DROP TYPE IF EXISTS public.user_role;
--
-- Name: user_role; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.user_role AS ENUM (
    'viewer',
    'admin'
);


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: camera_streams; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.camera_streams (
    stream_id integer NOT NULL,
    camera_id integer NOT NULL,
    run_id character varying(64) NOT NULL,
    source_type character varying(32) NOT NULL,
    source_ref character varying(255) NOT NULL,
    fps integer NOT NULL,
    s3_prefix character varying(255) NOT NULL,
    started_at timestamp without time zone NOT NULL,
    ended_at timestamp without time zone,
    is_active boolean NOT NULL
);


--
-- Name: camera_streams_stream_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.camera_streams_stream_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: camera_streams_stream_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.camera_streams_stream_id_seq OWNED BY public.camera_streams.stream_id;


--
-- Name: cameras; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cameras (
    camera_id integer NOT NULL,
    name character varying(100) NOT NULL,
    is_enabled boolean NOT NULL,
    lat double precision NOT NULL,
    lng double precision NOT NULL
);


--
-- Name: cameras_camera_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.cameras_camera_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: cameras_camera_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.cameras_camera_id_seq OWNED BY public.cameras.camera_id;


--
-- Name: detections; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.detections (
    detection_id integer NOT NULL,
    camera_id integer NOT NULL,
    track_id integer NOT NULL,
    coordinates json NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


--
-- Name: detections_detection_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.detections_detection_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: detections_detection_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.detections_detection_id_seq OWNED BY public.detections.detection_id;


--
-- Name: tracks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tracks (
    track_id integer NOT NULL,
    camera_id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


--
-- Name: tracks_track_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.tracks_track_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tracks_track_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.tracks_track_id_seq OWNED BY public.tracks.track_id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    user_id integer NOT NULL,
    email character varying(255) NOT NULL,
    username character varying(64) NOT NULL,
    password_hash character varying(255) NOT NULL,
    role public.user_role NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


--
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_user_id_seq OWNED BY public.users.user_id;


--
-- Name: camera_streams stream_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.camera_streams ALTER COLUMN stream_id SET DEFAULT nextval('public.camera_streams_stream_id_seq'::regclass);


--
-- Name: cameras camera_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cameras ALTER COLUMN camera_id SET DEFAULT nextval('public.cameras_camera_id_seq'::regclass);


--
-- Name: detections detection_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detections ALTER COLUMN detection_id SET DEFAULT nextval('public.detections_detection_id_seq'::regclass);


--
-- Name: tracks track_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tracks ALTER COLUMN track_id SET DEFAULT nextval('public.tracks_track_id_seq'::regclass);


--
-- Name: users user_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN user_id SET DEFAULT nextval('public.users_user_id_seq'::regclass);


--
-- Data for Name: camera_streams; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.camera_streams (stream_id, camera_id, run_id, source_type, source_ref, fps, s3_prefix, started_at, ended_at, is_active) FROM stdin;
3	2	run_cam02	VIDEO	cam_02	10	cam_02/run_cam02/	2026-01-30 19:57:05.464105	\N	t
4	3	run_cam03	VIDEO	cam_03	10	cam_03/run_cam03/	2026-01-30 19:57:05.464105	2026-02-01 08:04:34.102805	f
7	3	e5ced3468b2a4acf9e2eba436cea62b0	VIDEO	cam_3	10	3/e5ced3468b2a4acf9e2eba436cea62b0/	2026-02-01 10:08:21.937783	2026-02-01 10:08:26.613542	f
8	3	5731e9b4c9c74ab29df9c1e8d0f68a78	VIDEO	cam_3	10	3/5731e9b4c9c74ab29df9c1e8d0f68a78/	2026-02-01 10:08:27.424396	2026-02-01 10:08:29.023379	f
9	3	08a0ed83f8044b2799d0a8e62357df79	VIDEO	cam_3	10	3/08a0ed83f8044b2799d0a8e62357df79/	2026-02-01 10:09:22.132735	2026-02-01 10:09:24.260249	f
10	3	38970ba08ef241588dfea68910f51de2	VIDEO	cam_3	10	3/38970ba08ef241588dfea68910f51de2/	2026-02-01 10:24:37.961241	2026-02-01 10:24:41.270978	f
11	3	0512b9d1d3b643b7b307edc7c274daa6	VIDEO	cam_3	10	3/0512b9d1d3b643b7b307edc7c274daa6/	2026-02-01 10:31:51.644627	2026-02-01 10:32:15.156491	f
12	3	9e540a97a05b41d082ad3c862227fcfb	VIDEO	cam_3	10	3/9e540a97a05b41d082ad3c862227fcfb/	2026-02-01 10:33:57.959163	2026-02-01 10:34:01.876988	f
13	3	21aba2febcb04b3dbc493215f3e49c2b	VIDEO	cam_3	10	3/21aba2febcb04b3dbc493215f3e49c2b/	2026-02-01 10:35:25.31872	2026-02-01 10:35:33.584547	f
14	3	11d7a1e47e304d14973c47f74596f16d	VIDEO	cam_3	10	3/11d7a1e47e304d14973c47f74596f16d/	2026-02-01 10:37:47.493674	2026-02-01 10:38:01.474853	f
6	5	run_cam05	VIDEO	cam_05	10	cam_05/run_cam05/	2026-01-30 19:57:05.464105	2026-02-01 10:52:18.390783	f
15	5	5fb2689c4f314f24986bc1a6c99b8f02	VIDEO	cam_5	10	5/5fb2689c4f314f24986bc1a6c99b8f02/	2026-02-01 10:52:18.990609	2026-02-01 10:52:19.64856	f
16	3	08d496d3bd9d4b21aa237dcff15e9be9	VIDEO	cam_3	10	3/08d496d3bd9d4b21aa237dcff15e9be9/	2026-02-01 11:08:12.776823	2026-02-01 11:24:59.573465	f
17	3	79f0f103f4b1420f9ebfac3ccea74a5c	VIDEO	cam_3	10	3/79f0f103f4b1420f9ebfac3ccea74a5c/	2026-02-01 11:25:09.760896	2026-02-01 11:25:11.270085	f
18	3	4ef7ecd1d43c44e8a836a512be729388	VIDEO	cam_3	10	3/4ef7ecd1d43c44e8a836a512be729388/	2026-02-01 11:26:09.633761	2026-02-01 11:26:10.918502	f
19	3	f2cb770540774c90b48c622b654e4373	VIDEO	cam_3	10	3/f2cb770540774c90b48c622b654e4373/	2026-02-01 11:26:15.237546	2026-02-01 11:26:16.308014	f
20	3	3f5d77919cf24a0d8d1abc6512fe4a9e	VIDEO	cam_3	10	3/3f5d77919cf24a0d8d1abc6512fe4a9e/	2026-02-01 11:32:57.972178	2026-02-01 11:33:14.815391	f
21	3	055db93c483d45a1a688c8687dcc5fcd	VIDEO	cam_3	10	3/055db93c483d45a1a688c8687dcc5fcd/	2026-02-01 11:33:19.788051	2026-02-01 11:33:23.933905	f
22	3	ba4943093ac24d9c9ac1dfd2b69be8c8	VIDEO	cam_3	10	3/ba4943093ac24d9c9ac1dfd2b69be8c8/	2026-02-01 11:38:11.330795	2026-02-01 11:44:35.784302	f
23	3	43f24d7f18f74c91b553fe3ccba3e466	VIDEO	cam_3	10	3/43f24d7f18f74c91b553fe3ccba3e466/	2026-02-01 11:51:34.230442	2026-02-01 11:51:54.933859	f
24	3	c841422dbb3248f29420724a35b40408	VIDEO	cam_3	10	3/c841422dbb3248f29420724a35b40408/	2026-02-01 11:54:16.696039	2026-02-01 11:58:59.972738	f
25	3	7c1ac9a0a363416b9bf64611be7659ab	VIDEO	cam_3	10	3/7c1ac9a0a363416b9bf64611be7659ab/	2026-02-01 11:59:00.828094	2026-02-01 11:59:01.483639	f
26	3	a2ba59b932504f95a318abd05fd34e25	VIDEO	cam_3	10	3/a2ba59b932504f95a318abd05fd34e25/	2026-02-01 11:59:02.298314	2026-02-01 11:59:02.630923	f
27	3	a7d74086f1ea4e109c469f2048b3dd2c	VIDEO	cam_3	10	3/a7d74086f1ea4e109c469f2048b3dd2c/	2026-02-01 11:59:05.258693	2026-02-01 11:59:11.120526	f
28	3	2974ce8783124750bdfd713209a06481	VIDEO	cam_3	10	3/2974ce8783124750bdfd713209a06481/	2026-02-01 11:59:11.808345	2026-02-01 11:59:35.379197	f
29	3	caeb42df0ccb4a2e9e741aa749261922	VIDEO	cam_3	10	3/caeb42df0ccb4a2e9e741aa749261922/	2026-02-01 12:04:39.027342	2026-02-01 12:04:49.20315	f
30	3	ce4062ecf43f4584b5aa6db8610458e4	VIDEO	cam_3	10	3/ce4062ecf43f4584b5aa6db8610458e4/	2026-02-01 12:09:09.17772	2026-02-01 12:09:10.246154	f
31	3	e1e363c8f6474d05ab893701f3407d91	VIDEO	cam_3	10	3/e1e363c8f6474d05ab893701f3407d91/	2026-02-01 12:09:19.224134	2026-02-01 12:09:21.778572	f
32	3	f6c3ef6ce32c4890a2ac9eff628a20ce	VIDEO	cam_3	10	3/f6c3ef6ce32c4890a2ac9eff628a20ce/	2026-02-01 12:12:26.43276	2026-02-01 12:12:33.891957	f
33	3	a9b0d2631866427c8643fb8131990771	VIDEO	cam_3	10	3/a9b0d2631866427c8643fb8131990771/	2026-02-01 12:12:34.82824	2026-02-01 12:12:39.742588	f
2	1	run_cam01	VIDEO	cam_01	10	cam_01/run_cam01/	2026-01-30 19:57:05.464105	2026-02-01 12:13:11.544274	f
34	1	e92cc879788a4400a79a764871a53a03	VIDEO	cam_1	10	1/e92cc879788a4400a79a764871a53a03/	2026-02-01 12:13:12.075597	2026-02-01 12:13:16.436808	f
35	5	a283f1b0d41e43a9886dff9f2cdeead3	VIDEO	cam_5	10	5/a283f1b0d41e43a9886dff9f2cdeead3/	2026-02-01 12:13:20.776171	2026-02-01 12:13:24.07534	f
5	4	run_cam04	VIDEO	cam_04	10	cam_04/run_cam04/	2026-01-30 19:57:05.464105	2026-02-01 12:13:27.960733	f
36	4	959afd1f1dce47cf8f36cc7151bf346a	VIDEO	cam_4	10	4/959afd1f1dce47cf8f36cc7151bf346a/	2026-02-01 12:13:28.424078	2026-02-01 12:13:41.6696	f
37	4	dc271736ee3d422d91dee7120abda4be	VIDEO	cam_4	10	4/dc271736ee3d422d91dee7120abda4be/	2026-02-01 12:13:42.074457	2026-02-01 12:13:50.21657	f
38	4	0280140598594b3191f8c93528b2c746	VIDEO	cam_4	10	4/0280140598594b3191f8c93528b2c746/	2026-02-01 12:14:15.653297	2026-02-01 12:14:19.493228	f
39	4	c36853e6ad4042758c8531b709349f70	VIDEO	cam_4	10	4/c36853e6ad4042758c8531b709349f70/	2026-02-01 12:17:18.940312	2026-02-01 12:17:22.12108	f
40	1	1dececa0b531466d8f3e4fad7941eabf	VIDEO	cam_1	10	1/1dececa0b531466d8f3e4fad7941eabf/	2026-02-01 12:17:25.801639	2026-02-01 12:17:59.854624	f
41	3	3bf9452b1385401aa2f947fd50c2d72a	VIDEO	cam_3	10	3/3bf9452b1385401aa2f947fd50c2d72a/	2026-02-01 12:18:29.174177	2026-02-01 12:18:30.991173	f
42	4	bb28d57463064c86b0fe5f9df131f2cf	VIDEO	cam_4	10	4/bb28d57463064c86b0fe5f9df131f2cf/	2026-02-01 12:18:36.382625	2026-02-01 12:18:38.1884	f
43	1	5902f013fc994c29b70291efa1a2f520	VIDEO	cam_1	10	1/5902f013fc994c29b70291efa1a2f520/	2026-02-01 12:18:43.750508	2026-02-01 12:18:45.025246	f
44	1	4006f25ece814ad8a89f8530297550ac	VIDEO	cam_1	10	1/4006f25ece814ad8a89f8530297550ac/	2026-02-01 12:28:53.10769	2026-02-01 12:28:54.069255	f
45	5	4e58a656079a4d1a94e23589a719435e	VIDEO	cam_5	10	5/4e58a656079a4d1a94e23589a719435e/	2026-02-01 12:52:04.219296	2026-02-01 12:52:05.290237	f
46	3	38cc6a84f9ec44c18c6942e624a6bfd9	VIDEO	cam_3	10	3/38cc6a84f9ec44c18c6942e624a6bfd9/	2026-02-01 14:15:11.822735	2026-02-01 14:15:14.944471	f
47	3	61f3ac9124b541379dd6438137504dca	VIDEO	cam_3	10	3/61f3ac9124b541379dd6438137504dca/	2026-02-01 15:13:20.883648	2026-02-01 15:13:27.303676	f
48	3	399407630c184f9ca94267ace2d15680	VIDEO	cam_3	10	3/399407630c184f9ca94267ace2d15680/	2026-02-01 15:13:41.399835	2026-02-01 15:13:44.021883	f
49	3	7fa44028108543b3ba281bd7c748b9ce	VIDEO	cam_3	10	3/7fa44028108543b3ba281bd7c748b9ce/	2026-02-01 15:13:49.188104	2026-02-01 15:13:50.064878	f
50	3	2b706b193e1d45cd98c35381d6cd18b9	VIDEO	cam_3	10	3/2b706b193e1d45cd98c35381d6cd18b9/	2026-02-01 16:13:09.898217	2026-02-01 16:16:47.663635	f
51	3	365a82edf3c44f2a87ffc7aa6aac1d3b	VIDEO	cam_3	10	3/365a82edf3c44f2a87ffc7aa6aac1d3b/	2026-02-01 16:16:49.649283	2026-02-01 16:16:50.400572	f
52	3	361b4e0fb0d94eff93d1c6a0e780056e	VIDEO	cam_3	10	3/361b4e0fb0d94eff93d1c6a0e780056e/	2026-02-01 16:16:58.927738	2026-02-01 16:16:59.997648	f
53	3	fb6a14b4b6f54b9bb73f27b69023ecde	VIDEO	cam_3	10	3/fb6a14b4b6f54b9bb73f27b69023ecde/	2026-02-01 16:20:55.055856	2026-02-01 16:21:00.795298	f
54	3	a9feaba742034f83b7a27e3fffbae1ce	VIDEO	cam_3	10	3/a9feaba742034f83b7a27e3fffbae1ce/	2026-02-01 17:12:44.973893	2026-02-01 17:14:04.943052	f
55	3	8c92d9f836594f0b98c75d62f3b2d53b	VIDEO	cam_3	10	3/8c92d9f836594f0b98c75d62f3b2d53b/	2026-02-01 17:23:24.96419	2026-02-01 17:23:25.453026	f
56	3	1321a171cfbc40a2b47c3b78edd894cf	VIDEO	cam_3	10	3/1321a171cfbc40a2b47c3b78edd894cf/	2026-02-01 17:29:03.121868	2026-02-01 17:29:03.649777	f
57	3	c96623f2cbfe4179aec8d4ead049f441	VIDEO	cam_3	10	3/c96623f2cbfe4179aec8d4ead049f441/	2026-02-03 16:02:11.808712	2026-02-03 16:02:12.415922	f
58	3	74d11d284bba41d4b382c468edf5cd43	VIDEO	cam_3	10	3/74d11d284bba41d4b382c468edf5cd43/	2026-02-03 16:02:14.062006	2026-02-03 16:02:14.37185	f
59	3	54bdee60536c4536a7918db5ceb1c77b	VIDEO	cam_3	10	3/54bdee60536c4536a7918db5ceb1c77b/	2026-02-03 16:02:15.306823	2026-02-03 16:02:21.394075	f
60	3	ad5b3d6a37d64eaeacf34c5b2fe9f786	VIDEO	cam_3	10	3/ad5b3d6a37d64eaeacf34c5b2fe9f786/	2026-02-03 16:03:53.841514	2026-02-03 16:03:54.473865	f
\.


--
-- Data for Name: cameras; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.cameras (camera_id, name, is_enabled, lat, lng) FROM stdin;
1	Fire video 1	t	32.0853	34.7818
2	Fire video 2	t	32.1093	34.8555
3	Fire video 3	t	31.7683	35.2137
4	Fire video 4	t	32.794	34.9896
5	Fire video 5	t	31.0461	34.8516
\.


--
-- Data for Name: detections; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.detections (detection_id, camera_id, track_id, coordinates, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: tracks; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.tracks (track_id, camera_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (user_id, email, username, password_hash, role, is_active, created_at, updated_at) FROM stdin;
1	tedy@local.dev	tedy	$2b$12$KnqstxeVW5d66887dAx1NekRe.aCxpUEjVffLtMx5HekVEh.cazQ.	admin	t	2026-01-29 11:35:22.482893	2026-01-29 11:35:22.482895
\.


--
-- Name: camera_streams_stream_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.camera_streams_stream_id_seq', 60, true);


--
-- Name: cameras_camera_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.cameras_camera_id_seq', 5, true);


--
-- Name: detections_detection_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.detections_detection_id_seq', 1, false);


--
-- Name: tracks_track_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.tracks_track_id_seq', 1, false);


--
-- Name: users_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_user_id_seq', 1, true);


--
-- Name: camera_streams camera_streams_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.camera_streams
    ADD CONSTRAINT camera_streams_pkey PRIMARY KEY (stream_id);


--
-- Name: cameras cameras_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cameras
    ADD CONSTRAINT cameras_pkey PRIMARY KEY (camera_id);


--
-- Name: detections detections_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detections
    ADD CONSTRAINT detections_pkey PRIMARY KEY (detection_id);


--
-- Name: tracks tracks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tracks
    ADD CONSTRAINT tracks_pkey PRIMARY KEY (track_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_username; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username);


--
-- Name: camera_streams camera_streams_camera_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.camera_streams
    ADD CONSTRAINT camera_streams_camera_id_fkey FOREIGN KEY (camera_id) REFERENCES public.cameras(camera_id);


--
-- Name: detections detections_camera_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detections
    ADD CONSTRAINT detections_camera_id_fkey FOREIGN KEY (camera_id) REFERENCES public.cameras(camera_id) ON DELETE CASCADE;


--
-- Name: detections detections_track_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detections
    ADD CONSTRAINT detections_track_id_fkey FOREIGN KEY (track_id) REFERENCES public.tracks(track_id) ON DELETE CASCADE;


--
-- Name: tracks tracks_camera_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tracks
    ADD CONSTRAINT tracks_camera_id_fkey FOREIGN KEY (camera_id) REFERENCES public.cameras(camera_id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict 2b40HfTyMnaefHUZJRS2Pv476xXqF6doZQBsTBfyY3VA6ViMQtNzEqd3GtYRIyE

