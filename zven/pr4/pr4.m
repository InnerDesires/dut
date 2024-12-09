function plotchar(data)
    % PLOTCHAR Візуалізує 35-елементний вектор як 5x7 матрицю
    % Вхід: data - вектор із 35 елементів

    % Перевірка, що вхід має саме 35 елементів
    if numel(data) ~= 35
        error('Input vector must have exactly 35 elements for a 5x7 grid.');
    end

    % Перетворення вектора на 5x7 матрицю (з транспонуванням для правильної орієнтації)
    charMatrix = reshape(data, [5, 7])';

    % Візуалізація матриці як зображення
    imagesc(charMatrix); % Відображення матриці
    colormap(gray); % Використання чорно-білої палітри
    axis off; % Відключення осей
    axis equal; % Квадратні пікселі
end
% Завантаження алфавіту з файлу Alphabet.csv
alphabet = csvread('Alphabet.csv');

% Вибір символів для варіанту (M, W, H)
L1 = alphabet(:, 1); % Символ M
L2 = alphabet(:, 2); % Символ W
L3 = alphabet(:, 3); % Символ H

% Візуалізація вибраних символів
figure;
subplot(1,3,1); plotchar(L1);
title('Letter M');
subplot(1,3,2); plotchar(L2);
title('Letter W');
subplot(1,3,3); plotchar(L3);
title('Letter H');

% Створення мережі Хопфілда
T = [L1, L2, L3]; % Комбінування символів у матрицю цілей
net = newhop(T);


% Спотворення символів (додавання шуму)
noisyL1 = L1 + randn(35,1) * 0.4; % Спотворений символ M
noisyL2 = L2 + randn(35,1) * 0.4; % Спотворений символ W

% Розпізнавання спотворених символів
[Y1, ~, ~] = sim(net, 1, {}, noisyL1);
[Y2, ~, ~] = sim(net, 1, {}, noisyL2);

% Візуалізація результатів розпізнавання
figure;
subplot(2,2,1); plotchar(noisyL1);
title('Noisy M');
subplot(2,2,2); plotchar(Y1);
title('Recognized M');
subplot(2,2,3); plotchar(noisyL2);
title('Noisy W');
subplot(2,2,4); plotchar(Y2);
title('Recognized W');

% Тестування нового символу, який не був у навчальній вибірці
Lnew = alphabet(:, 3) + randn(35,1) * 0.8; % Спотворений символ H
[Ynew, ~, ~] = sim(net, 1, {}, Lnew);

% Візуалізація результату для нового символу
figure;
subplot(1,2,1); plotchar(Lnew);
title('Noisy H');
subplot(1,2,2); plotchar(Ynew);
title('Recognized (or not)');
