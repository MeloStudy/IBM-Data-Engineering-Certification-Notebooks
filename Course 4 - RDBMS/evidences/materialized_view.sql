CREATE MATERIALIZED VIEW public."product_info_m-view" AS 
	SELECT 
		p.product_name, 
		p.description, 
		t.product_category
	FROM public.product p
	JOIN public.product_type t
	ON p.product_type_id = t.product_type_id;