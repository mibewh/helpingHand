CREATE OR REPLACE FUNCTION
	sp_get_worker_service_requests(p_worker_username VARCHAR(20))
	RETURNS TABLE(
		client_username VARCHAR(20),
		title VARCHAR(50),
		description TEXT,
		schedule TEXT,
		address VARCHAR(100)
	)
	LANGUAGE plpgsql
AS $function$

BEGIN
	RETURN QUERY
		SELECT
			cl.client_username,
			sr.title,
			sr.description,
			sr.schedule,
			sr.address
		FROM
			client cl,
			service_request sr,
			worker_request wr
		WHERE
			sr.service_id = wr.service_id AND
			sr.client_username = cl.client_username AND
			wr.worker_username = p_worker_username;
END;

$function$;
	