program forLoop;
var x, y, s: integer;
begin
    s := 0;
    y := 2;

	for x := 0 To 10 do
	begin
		s := 1;
		s := 2;
	end;

	for x := 0 To 10 do
	begin
		s := s + x;
        s := s + y;
		writeln(s);
	end;
end.