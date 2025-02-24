function z = fitnessFunction(x)
    % Цільова функція для оптимізації
    z = x(1) * exp(-(x(1)^2 + x(2)^2));
end

% Побудова графіка функції
[X, Y] = meshgrid(-2:0.1:2, -2:0.1:2);
Z = X .* exp(-(X.^2 + Y.^2));

% Відображення поверхні
figure;
surf(X, Y, Z);
title('Графік функції z(x, y)');
xlabel('x');
ylabel('y');
zlabel('z(x, y)');

% Відображення поверхні
figure;
surf(X, Y, Z);
title('Графік функції z(x, y)');
xlabel('x');
ylabel('y');
zlabel('z(x, y)');

% Кількість змінних
nvars = 2;

% Налаштування параметрів ГА
options = optimoptions('ga', ...
    'PopulationSize', 50, ...          % Розмір популяції
    'MaxGenerations', 100, ...         % Кількість поколінь
    'CrossoverFraction', 0.8, ...      % Частка схрещувань
    'MutationFcn', @mutationgaussian, ... % Мутація Гаусса
    'SelectionFcn', @selectionroulette, ... % Рулетковий відбір
    'PlotFcn', {@gaplotbestf, @gaplotdistance}); % Графіки

% Виклик генетичного алгоритму
[x, fval] = ga(@fitnessFunction, nvars, [], [], [], [], ...
    [-5, -5], [5, 5], [], options);

% Результати
disp('Оптимальні значення:');
disp(['x = ', num2str(x(1)), ', y = ', num2str(x(2))]);
disp(['Мінімум функції: ', num2str(fval)]);