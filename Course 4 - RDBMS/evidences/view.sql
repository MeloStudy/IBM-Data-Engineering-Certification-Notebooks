CREATE VIEW public.staff_locations_view AS
	SELECT staff_id,
	first_name,
	last_name,
	location
	FROM public.staff
	WHERE "position" NOT IN ('CEO', 'CFO');