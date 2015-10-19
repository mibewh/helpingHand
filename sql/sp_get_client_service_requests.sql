CREATE OR REPLACE FUNCTION
	sp_get_client_service_requests(p_client_username character varying)
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
		WHERE sr.client_username = p_client_username;
END;

$function$;
