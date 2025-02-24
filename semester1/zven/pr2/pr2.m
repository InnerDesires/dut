% Вхідні дані
P = [-2:0.2:1.4];
T = cos(P + 0.05 * randn(size(P))) + 0.04; % Вектор цілей

% Створення RBF-мережі
spread = 0.5; % Параметр впливу
net = newrbe(P, T, spread);

% Результати моделювання
V = sim(net, P);

% Графік результатів
figure;
plot(P, T, 'r*', 'DisplayName', 'Цільові дані');
hold on;
plot(P, V, 'bo', 'DisplayName', 'Модельовані дані');
legend;
title('Базисна мережа з нульовою помилкою');
grid on;

% Генерація даних
x = -10:0.1:10;
y = zeros(size(x));
for i = 1:length(x)
    if x(i) == 0
        y(i) = 1;  % Handle the case when x = 0
    else
        y(i) = sin(x(i))/x(i);
    end
end

% Створення RBF-мережі
spread = 0.8;  % Adjusted spread
net = newrb(x, y, 0.01, spread, 50);  % Added maximum neurons parameter

% Моделювання
y_pred = sim(net, x);

% Графік
figure;
plot(x, y, 'b-', 'DisplayName', 'Оригінальна функція');
hold on;
plot(x, y_pred, 'r--', 'DisplayName', 'Апроксимація');
legend;
title('Апроксимація функції y = sin(x)/x радіальною базисною мережею');
grid on;

% Вхідні дані
p = -3:0.1:3;
a1 = radbas(p);
a2 = radbas(p - 1.5);
a3 = radbas(p + 2);

% Зважена сума
a = a1 + a2 * 1 + a3 * 0.5;

% Графіки
figure;
plot(p, a1, 'b-', 'DisplayName', 'Функція 1');
hold on;
plot(p, a2, 'r--', 'DisplayName', 'Функція 2');
plot(p, a3 * 0.5, 'g-.', 'DisplayName', 'Функція 3');
plot(p, a, 'k-', 'DisplayName', 'Зважена сума');
legend;
title('Графіки радіальних базисних функцій');
grid on;
