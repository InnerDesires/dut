% Зчитування даних із файлу CSV
data = csvread('function_data.csv', 1, 0); % Пропустити перший рядок (заголовки)
x = data(:, 1); % Перший стовпець - значення x
y = data(:, 2); % Другий стовпець - значення y

% Побудова графіка
figure;
plot(x, y, 'b-');
title('Функція y = sin(x)/x');
xlabel('x');
ylabel('y');
grid on;

% Створення нейронної мережі
hiddenLayerSize = [5, 3]; % Два прихованих шари: 5 і 3 нейрони
net = fitnet(hiddenLayerSize, 'trainlm'); % Активація: logsig, навчання: Levenberg-Marquardt

% Розподіл вибірки
net.divideParam.trainRatio = 0.7; % 70% на навчання
net.divideParam.valRatio = 0.2;   % 20% на валідацію
net.divideParam.testRatio = 0.1;  % 10% на тестування

% Навчання мережі
[net, tr] = train(net, x', y');

% Тестування мережі
y_pred = net(x');

% Побудова графіка апроксимованих даних
figure;
plot(x, y, 'b-', 'DisplayName', 'Вихідна функція');
hold on;
plot(x, y_pred, 'r--', 'DisplayName', 'Апроксимація');
legend;
title('Апроксимація функції');
xlabel('x');
ylabel('y');
grid on;
hold off;

% Помилки
trainError = perform(net, y(tr.trainInd)', net(x(tr.trainInd)'));
valError = perform(net, y(tr.valInd)', net(x(tr.valInd)'));
testError = perform(net, y(tr.testInd)', net(x(tr.testInd)'));

fprintf('Train Error: %.4f\n', trainError);
fprintf('Validation Error: %.4f\n', valError);
fprintf('Test Error: %.4f\n', testError);

save('trained_network.mat', 'net');