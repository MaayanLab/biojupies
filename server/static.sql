INSERT INTO `parameter` (`id`, `parameter_name`, `parameter_description`, `parameter_string`, `tool_fk`)
VALUES
	(17, 'Plot Type', 'Whether to display the plot statically or interactively.', 'plot_type', 1),
	(18, 'Plot Type', 'Whether to display the plot statically or interactively.', 'plot_type', 4),
	(19, 'Plot Type', 'Whether to display the plot statically or interactively.', 'plot_type', 6),
	(20, 'Plot Type', 'Whether to display the plot statically or interactively.', 'plot_type', 7),
	(21, 'Plot Type', 'Whether to display the plot statically or interactively.', 'plot_type', 9),
	(22, 'Plot Type', 'Whether to display the plot statically or interactively.', 'plot_type', 10),
	(23, 'Plot Type', 'Whether to display the plot statically or interactively.', 'plot_type', 14);

INSERT INTO `parameter_value` (`id`, `parameter_fk`, `value`, `type`, `default`)
VALUES
	(50, 17, 'interactive', 'str', 1),
	(51, 18, 'interactive', 'str', 1),
	(52, 19, 'interactive', 'str', 1),
	(53, 20, 'interactive', 'str', 1),
	(54, 21, 'interactive', 'str', 1),
	(55, 22, 'interactive', 'str', 1),
	(56, 23, 'interactive', 'str', 1);
