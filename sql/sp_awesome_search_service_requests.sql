CREATE OR REPLACE FUNCTION
	sp_awesome_search_service_requests(p_search_term TEXT)
	RETURNS TABLE(
		title VARCHAR(50),
		description TEXT,
		schedule TEXT,
		address VARCHAR(100)
	)
	LANGUAGE plpgsql
AS $function$

BEGIN
	RETURN QUERY
		SELECT sr.title, sr.description, sr.schedule, sr.address
		FROM service_request sr
		WHERE
			sr.title LIKE '%'||p_search_term||'%' OR
			sr.description LIKE '%'||p_search_term||'%' OR
			sr.address LIKE '%'||p_search_term||'%';
END;

$function$;
	